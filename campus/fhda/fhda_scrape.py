import re
import json
import argparse
from os.path import join
from copy import deepcopy
from collections import defaultdict
from shutil import move

from titlecase import titlecase

from logger import log_err, log_warn, log_info
from data.utils import list_dbs
from scraper.ssb_base import BaseHooks
from scraper.ssb_auth_schedule import AdvancedScraper
from scraper.ssb_public_schedule import ScheduleScraper

from .fhda_login import login
from .fhda_settings import SSB_URL, DB_DIR, CACHE_DIR
from .fhda_utils import clean_course_name_str
from .fhda_scrape_seats import scrape_seats


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


def write_metadata():
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

    log_info('Dumped metadata')


def run_advanced_scraper(**kwargs):
    try:
        scraper = AdvancedScraper(
            ssb_url=SSB_URL,
            db_dir=DB_DIR,
            cache_dir=CACHE_DIR,
            hooks=FHDAScraperHooks,
            login=login,

            trace=True,
            **kwargs,
        )
        scraper.run()

    except KeyboardInterrupt:
        log_err('Aborted advanced schedule scraper', start='\n')


def run_public_schedule_scraper(**kwargs):
    if not kwargs.get('db_dir'):
        kwargs['db_dir'] = DB_DIR

    try:
        scraper = ScheduleScraper(
            ssb_url=SSB_URL,
            cache_dir=CACHE_DIR,
            hooks=FHDAScraperHooks,
            # login=login,

            trace=True,
            **kwargs,
        )
        scraper.run()

    except KeyboardInterrupt:
        log_err('Aborted public schedule scraper', start='\n')


if __name__ == '__main__':
    ENABLE_ADVANCED = False
    ENABLE_SCHEDULE = True
    ENABLE_SEATS = True

    parser = argparse.ArgumentParser(description='Scrape FHDA data')
    parser.add_argument('--update', default=False, action='store_true',
                        help='Update data with seat info')
    args = parser.parse_args()

    if args.update:
        temp_dir = join(DB_DIR, 'temp')
        run_public_schedule_scraper(
            db_dir=temp_dir,
            max_terms=2,
            use_cache=False
        )
        write_metadata()
        terms = scrape_seats(db_dir=temp_dir, prefix='sched_')

        for term in terms:
            filename = f'sched_{term}_database.json'
            move(join(temp_dir, filename), join(DB_DIR, filename))

    else:
        if ENABLE_ADVANCED:
            run_advanced_scraper(
                max_terms=12,
                # use_cache=False,
                start_term='202132',
            )
        if ENABLE_SCHEDULE:
            run_public_schedule_scraper(
                max_terms=2,
                # use_cache=False,
                # start_term='202042',
            )
        if ENABLE_SEATS:
            scrape_seats(db_dir=DB_DIR)

        write_metadata()
