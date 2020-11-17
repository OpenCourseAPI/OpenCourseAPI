import json
from os.path import join

from tinydb import TinyDB

from common import ApiError

from .wvm_settings import DB_DIR, CURRENT_YEAR, CURRENT_TERM, CURRENT_TERM_CODES


class WVMCampus:
    CAMPUS = ['wv', 'mn']
    QUARTER_TO_NUM = {
        'winter': 1,
        'spring': 3,
        'summer': 5,
        'fall': 7,
    }
    NUM_TO_QUARTER = {v: k for k, v in QUARTER_TO_NUM.items()}
    CAMPUS_TO_PREFIX = {
        'wv': 'wvc',
        'mc': 'mc',
    }

    def load_db(self, campus, year, quarter):
        if quarter not in self.QUARTER_TO_NUM:
            raise ApiError(
                404,
                f'Invalid quarter name. Possible quarters are {", ".join(self.QUARTER_TO_NUM.keys())}'
            )

        name = f'{self.CAMPUS_TO_PREFIX[campus]}_{year}{self.QUARTER_TO_NUM[quarter]}0'

        try:
            db = TinyDB(join(DB_DIR, f'sched_{name}_database.json'), access_mode='r')
        except FileNotFoundError:
            raise FileNotFoundError

        return db

    def get_current_term(self, campus):
        return {'year': CURRENT_YEAR, 'term': CURRENT_TERM, 'code': CURRENT_TERM_CODES[campus]}

    def list_dbs(self, campus):
        with open(join(DB_DIR, 'metadata.json'), 'r') as file:
            metadata = json.loads(file.read())
            prettyTerms = []

            for info in metadata['terms']:
                term_campus = info['campus']
                term = info['code']

                if term_campus != self.CAMPUS_TO_PREFIX[campus]:
                    continue

                year = int(term[0:4])
                quarter = self.NUM_TO_QUARTER[int(term[4])]

                prettyTerms.append({'year': year, 'term': quarter, 'code': term})

            return prettyTerms


wvm_campus = WVMCampus()
