import re
import json
from os.path import join
from copy import deepcopy
from collections import defaultdict

from tinydb import TinyDB, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from logger import log_err
from data.utils import list_dbs
from scraper.ssb_base import BaseHooks
from scraper.ssb_auth_schedule import AdvancedScraper
from scraper.ssb_public_schedule import ScheduleScraper
from scraper.postprocess import postprocess_dbs

from .wvm_settings import SSB_URL, DB_DIR, CACHE_DIR, NUM_TO_QUARTER, PREFIX_TO_CAMPUS


def clean_dept_name(name: str):
    '''
    Remove the trailing " - WVC" / " - MC" from department titles
    Ex. "Accounting - WVC"
    '''
    return re.sub(r'^(.*\w) ?- ?[WVMC]{2,3}$', r'\1', name)


def get_term_info(campus):
    def get_info(term):
        year = int(term[0:4])
        quarter = NUM_TO_QUARTER[int(term[4])]
        return year, quarter, PREFIX_TO_CAMPUS[campus]
    return get_info


def load_db(term, tag, campus, readonly=False):
    db_path = join(DB_DIR, f'{tag}_{campus}_{term}_database.json')

    if readonly:
        return TinyDB(db_path, access_mode='r', storage=CachingMiddleware(JSONStorage))
    else:
        return TinyDB(db_path)


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
                # trace=True,
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

    ddd = defaultdict(lambda: defaultdict(list))

    for info in termdbs:
        ddd[info['campus']][info['code']] = ['sched']

    for campus, term_dbs in ddd.items():
        db = TinyDB(join(DB_DIR, f'multi_{campus}_database.json'))
        postprocess_dbs(db, term_dbs, campus=campus, get_term_info=get_term_info(campus), load_db=load_db)
