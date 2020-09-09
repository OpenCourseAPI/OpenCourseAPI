import re
import json
from os.path import join
from copy import deepcopy
from collections import defaultdict

from titlecase import titlecase
from tinydb import TinyDB, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from logger import log, log_info, log_err, log_warn
from data.utils import list_dbs
from scraper.ssb_base import BaseHooks
from scraper.ssb_auth_schedule import AdvancedScraper
from scraper.ssb_public_schedule import ScheduleScraper
from scraper.postprocess import postprocess_dbs

from .fhda_login import login
from .fhda_settings import SSB_URL, DB_DIR, CACHE_DIR, NUM_TO_QUARTER, NUM_TO_CAMPUS
from .fhda_utils import clean_course_name_str

ENABLE_ADVANCED = True
ENABLE_SCHEDULE = True


def fix_title(title: str):
    '''
    Clean and change text case of Foothill College course titles
    '''
    title = re.sub(r'(\w):(\w)', r'\1: \2', title)
    title = re.sub(r'(\w),(\w)', r'\1, \2', title)
    title = titlecase(title)
    title = re.sub(r'(\b)(Ii|Iii|Iv|v|Ia|Ib)(\b)', lambda match: f'{match.groups()[0]}{match.groups()[1].upper()}{match.groups()[2]}', title)
    return title


def clean_dept_name(name: str):
    '''
    Remove the trailing "-FH" / "-FD" / "-DA" from department titles
    Ex. "Accounting-FD"
    '''
    return re.sub(r'^(.*\w)-[FHDA]{2}$', r'\1', name)


def get_term_info(term):
    year = int(term[0:4])
    quarter_num = int(term[4])
    quarter = NUM_TO_QUARTER[quarter_num]
    term_campus = NUM_TO_CAMPUS[int(term[5])]

    if quarter_num < 3:
        # If the quarter is summer or fall, then the year should be incremented
        # Ex. Fall 2020 => 20212X
        year -= 1

    return year, quarter, term_campus


def load_db(term, tag, campus, readonly=False):
    db_path = join(DB_DIR, f'{tag}_{term}_database.json')

    if readonly:
        return TinyDB(db_path, access_mode='r', storage=CachingMiddleware(JSONStorage))
    else:
        return TinyDB(db_path)


class FHDAScraperHooks(BaseHooks):
    @staticmethod
    def transform_depts(depts):
        for dept_id, dept_name in depts.items():
            # Remove the trailing "-FH" / "-FD" / "-DA" from department titles
            depts[dept_id] = clean_dept_name(dept_name)

        return depts

    @staticmethod
    def transform_class(class_data):
        class_data = deepcopy(class_data)
        course = class_data['course']
        title = class_data['title']

        if title.isupper():
            # Foothill College titles and past De Anza ones are unfortunately all caps
            class_data['title'] = fix_title(title)

        class_data['course'] = clean_course_name_str(course)

        mapping = {
            # 'De Anza, Main Campus': {'DA'},
            # 'De Anza, Off Campus': {'DO', 'DA'}
            # 'Foothill Sunnyvale Center': {'FC', 'FH'},
            # 'Foothill, Main Campus': {'FO', 'FH'},
            # 'Foothill, Off Campus': {'FO', 'FH'},
            # '': {'FO', 'FH'}
            'De Anza, Main Campus': 'DA',
            'De Anza, Off Campus': 'DO',
            'Foothill Sunnyvale Center': 'FC',
            'Foothill, Main Campus': 'FH',
            'Foothill, Off Campus': 'FO'
        }

        for idx, time in enumerate(class_data['times']):
            campus = time.get('campus')

            if campus and campus not in mapping.values():
                if mapping.get(campus) != None:
                    time['campus'] = mapping.get(campus)
                else:
                    replaced = False

                    for full_str in mapping.keys():
                        if full_str in campus:
                            replaced = True
                            time['campus'] = mapping.get(full_str)
                            break

                    if not replaced:
                        log_warn(f'Unknown campus string for {class_data["CRN"]} {campus}')

        return class_data


if __name__ == '__main__':
    if ENABLE_ADVANCED:
        try:
            scraper = AdvancedScraper(
                ssb_url=SSB_URL,
                db_dir=DB_DIR,
                cache_dir=CACHE_DIR,
                hooks=FHDAScraperHooks,
                login=login,

                max_terms=8,
                # use_cache=False,
                # start_term='202042',
                # trace=True,
            )
            scraper.run()

        except KeyboardInterrupt:
            log_err('Aborted', start='\n')

    if ENABLE_SCHEDULE:
        try:
            scraper = ScheduleScraper(
                # ssb_url='https://banssb.western.edu/WOL'
                # ssb_url='https://bannerssb.utk.edu/kbanpr'
                # ssb_url='https://ssb-prod.ec.wvm.edu/PROD'
                ssb_url=SSB_URL,
                db_dir=DB_DIR,
                cache_dir=CACHE_DIR,
                hooks=FHDAScraperHooks,
                # login=login,

                max_terms=8,
                # use_cache=False,
                # start_term='202111',
                # trace=True,
            )
            scraper.run()

        except KeyboardInterrupt:
            log_err('Aborted', start='\n')

    db_files = list_dbs(DB_DIR, filter=r'(sched|new)_[0-9]{6}_database.json$')

    tagdbs = defaultdict(list)
    termdbs = defaultdict(list)

    for filepath in db_files:
        matches = re.search(r'(\w*?)_([0-9]{6})_database.json$', filepath)
        if matches and matches.groups():
            tag, term = matches.groups()
            tagdbs[tag].append(term)
            termdbs[term].append(tag)

    with open(join(DB_DIR, 'metadata.json'), 'w') as outfile:
        json.dump({'tags': dict(tagdbs), 'terms': dict(termdbs)}, outfile)

    db = TinyDB(join(DB_DIR, 'multi_database.json'))
    postprocess_dbs(db, termdbs, get_term_info=get_term_info, load_db=load_db)
