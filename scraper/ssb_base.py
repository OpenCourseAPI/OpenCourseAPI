import re
from os import makedirs
from os.path import join, exists
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB
from marshmallow import ValidationError as MarshValidationError

from logger import log, log_info, log_warn, log_trace
from data.models import classDataSchema, classTimeSchema

SOUP_PARSER = 'lxml'


class BaseHooks:
    DATE_FORMAT = '%b %d, %Y' # '%d-%b-%Y'

    @staticmethod
    def transform_depts(depts):
        return depts

    @staticmethod
    def transform_class(class_data):
        return class_data

    @classmethod
    def parse_date(cls, date_str):
        return datetime.strftime(datetime.strptime(date_str, cls.DATE_FORMAT), '%m/%d/%Y')

    @staticmethod
    def clean_units_str(units_str):
        if 'TO' in units_str:
            splitted = units_str.split('TO')
            return splitted[-1].strip()

        elif 'OR' in units_str:
            splitted = units_str.split('OR')
            return splitted[-1].strip()

        else:
            return units_str

    @staticmethod
    def clean_instructor_name(name):
        # Replace ', ' with '', '(P)' with '', '   ' (n spaces) with ' ' (one space)
        return re.sub(r'\s+', ' ', re.sub(r'(?:, )|(?:\(\w?\))', '', name)).strip()


class BaseSSBScraper:
    PREFIX = ''

    def __init__(self, ssb_url, db_dir, cache_dir, hooks=None, login=None, ssb_campus=None, max_terms=-1, start_term=None, use_cache=True, trace=False):
        self.ssb_url = ssb_url
        self.db_dir = db_dir
        self.cache_dir = cache_dir
        self.login = login
        self.ssb_campus = ssb_campus
        self.hooks = hooks or BaseHooks

        self.max_terms = max_terms
        self.start_term = start_term
        self.use_cache = use_cache
        self.trace = trace

        self.loggedIn = False
        self.session = requests.session()

    def run(self):
        # Create db dir (ex. 'db/') and cache dir (ex. 'db/.cache/scrape_advanced')
        for folder in [self.db_dir, self.cache_dir]:
            if not exists(folder):
                makedirs(folder, exist_ok=True)

        # Get all term codes (hits FHDA endpoint)
        codes = self.mine_term_codes()

        # Debug utilities to limit the terms mined
        if self.start_term and codes.index(self.start_term):
            codes = codes[codes.index(self.start_term):]
        if self.max_terms > 0 and len(codes) > self.max_terms:
            codes = codes[:self.max_terms]

        log_info(f'Loaded {len(codes)} term codes')

        for term in codes:
            # Mine department data
            # Hits FHDA endpoint to get all departments for the term
            log(term, 'magenta', 'Mining departments...       ', end='\r')
            depts = self.mine_dept_data(term)

            # Mine and process class data
            # Hits FHDA endpoint to get all classes for the term
            log(term, 'magenta', 'Mining classes...           ', end='\r')
            classes = self.mine_campus_term(term, depts)

            # Create / load a DB for the term
            log(term, 'magenta', 'Writing data to db...       ', end='\r')
            campus_prefix = f'{self.ssb_campus.lower()}_' if self.ssb_campus else ''
            db = TinyDB(join(self.db_dir, f'{self.PREFIX}{campus_prefix}{term}_database.json'))

            with db:
                # Write the dept and class data to the DB
                self.save_classes(db, depts, classes)

                # Get counts of mined data (for logging)
                dept_count = len(db.table('departments'))
                course_count = len(db.table('courses'))
                class_count = len(db.table('classes'))

            # that's it! move on to the next term code...
            info = f'Mined {dept_count} depts, {course_count} courses, and {class_count} classes'
            log(term, 'magenta', f'{info}                   ')

    def mine_term_codes(self):
        '''
        Mine term codes will grab all the term IDs.

        :param use_cache: (bool) whether to use the cache
        :return data: (list) list of term codes
        '''
        html = self.fetch_and_cache(
            'bwckschd.p_disp_dyn_sched',
            'all-terms.html',
        )
        soup = BeautifulSoup(html, SOUP_PARSER)

        term_select = soup.find('select', {'name': 'p_term'})
        options = term_select.find_all('option')

        return [opt['value'] for opt in options if opt['value']]

    def mine_dept_data(self, term: str):
        '''
        Mine dept data will grab the department IDs for a given quarter.

        :param term: (str) the term to mine
        :param use_cache: (bool) whether to use the cache
        :return data (list(tuple)) the html body
        '''
        data = [('p_calling_proc', 'bwckschd.p_disp_dyn_sched'), ('p_term', term)]

        html = self.fetch_and_cache(
            'bwckgens.p_proc_term_date',
            f'{term}-depts.html',
            data=data,
        )
        soup = BeautifulSoup(html, SOUP_PARSER)

        dept_select = soup.find('select', {'id': 'subj_id'})
        options = dept_select.find_all('option')
        depts = {}

        for option in options:
            dept_id = option['value']

            if dept_id:
                depts[dept_id] = option.get_text().strip() or ''

        return self.hooks.transform_depts(depts)

    def save_classes(self, db, depts, classes):
        db_depts = []
        db_courses = []
        db_classes = []

        depts = {k.replace(' ', ''): v for k, v in depts.items()}

        for dept, t in classes.items():
            db_depts.append({
                'id': dept,
                'name': depts[dept],
            })

            for course, section in t.items():
                course_classes = []
                course_titles = set()

                for cl in section.values():
                    try:
                        data = classDataSchema.load(cl)
                        classTimes = [classTimeSchema.load(time) for time in cl['times']]
                    except MarshValidationError as e:
                        print(e, cl)
                        continue

                    data['times'] = classTimes
                    db_classes.append(data)
                    course_titles.add(data['title'])
                    course_classes.append(data['CRN'])

                if len(course_titles) > 1:
                    log_warn(f'Multiple course titles for "{dept} {course}" {str(course_titles)}')

                db_courses.append({
                    'dept': dept,
                    'course': course,
                    'title': course_titles.pop(),
                    'classes': course_classes
                })

        db.drop_tables()
        db.table('departments').insert_multiple(db_depts)
        db.table('courses').insert_multiple(db_courses)
        db.table('classes').insert_multiple(db_classes)

    def fetch_and_cache(self, url: str, filename: str, authenticated=False, data=None):
        full_filename = join(self.cache_dir, filename)

        if self.use_cache:
            try:
                with open(full_filename, 'r') as f:
                    if self.trace:
                        log_trace(f'Loaded {url} from cache')
                    return f.read()
            except FileNotFoundError:
                pass

        if self.trace:
            log_trace(f'Loading {url} from network...')

        if authenticated:
            self.do_login()

        obj = self.session if authenticated else requests
        res = obj.post(self.ssb_url + url, data=data) if data else obj.get(self.ssb_url + url)
        res.raise_for_status()

        with open(full_filename, 'wb') as file:
            file.write(res.content)

        return res.content

    def do_login(self):
        if not self.loggedIn and self.login:
            self.login(self.session)
            self.loggedIn = True
            log_info('Logged in')
