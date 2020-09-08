import re
import json
from os.path import join
from copy import deepcopy

from logger import log_err
from data.utils import list_dbs
from scraper.ssb_base import BaseHooks
from scraper.ssb_auth_schedule import AdvancedScraper
from scraper.ssb_public_schedule import ScheduleScraper

from .wvm_settings import SSB_URL, DB_DIR, CACHE_DIR


def clean_dept_name(name: str):
    '''
    Remove the trailing " - WVC" / " - MC" from department titles
    Ex. "Accounting - WVC"
    '''
    return re.sub(r'^(.*\w) ?- ?[WVMC]{2,3}$', r'\1', name)


class WVMScraperHooks(BaseHooks):
    @staticmethod
    def transform_depts(depts):
        for dept_id, dept_name in depts.items():
            # Remove the trailing " - WVC" / " - MC" from department titles
            # Ex. "Accounting - WVC"
            depts[dept_id] = clean_dept_name(dept_name)

        return depts

    @staticmethod
    def transform_class(class_data):
        class_data = deepcopy(class_data)

        # Replace leading 0's from course name
        class_data['course'] = re.sub(r'0*(.*)$', r'\1', class_data['course'])

        # Titles look something like "Intro to Accounting     (1.5 Lecture)"
        # TODO: the information in the parenthesis can be extracted and saved
        class_data['title'] = re.sub(r'\(.*\)', '', class_data['title']).strip()

        return class_data


if __name__ == '__main__':
    try:
        for ssb_campus in ['MC', 'WVC']:
            scraper = ScheduleScraper(
                ssb_url=SSB_URL,
                db_dir=DB_DIR,
                cache_dir=CACHE_DIR,
                ssb_campus=ssb_campus,
                hooks=WVMScraperHooks,

                # max_terms=4,
                # use_cache=False,
                # start_term='201231',
                trace=True,
            )
            scraper.run()

    except KeyboardInterrupt:
        log_err('Aborted', start='\n')

    db_files = list_dbs(DB_DIR, prefix=f'sched_')
    termdbs = []

    for filepath in db_files:
        matches = re.search(r'sched_(\w{2,3})_([0-9]{6})_database.json$', filepath)
        if matches and matches.groups():
            campus, term = matches.groups()
            termdbs.append({'campus': campus, 'code': term})

    with open(join(DB_DIR, 'metadata.json'), 'w') as outfile:
        json.dump({'terms': termdbs}, outfile)
