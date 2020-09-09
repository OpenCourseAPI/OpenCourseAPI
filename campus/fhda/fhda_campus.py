import json
from os.path import join

from tinydb import TinyDB

from common import ApiError
from .fhda_settings import DB_DIR


class FHDACampus:
    CAMPUS = ['fh', 'da']
    QUARTER_TO_NUM = {
        'summer': 1,
        'fall': 2,
        'winter': 3,
        'spring': 4
    }
    NUM_TO_QUARTER = {v: k for k, v in QUARTER_TO_NUM.items()}
    CAMPUS_TO_NUM = {
        'fh': 1,
        'da': 2
    }
    NUM_TO_CAMPUS = {v: k for k, v in CAMPUS_TO_NUM.items()}

    def load_db(self, campus, year, quarter):
        if quarter not in self.QUARTER_TO_NUM:
            raise ApiError(
                404,
                f'Invalid quarter name. Possible quarters are {", ".join(self.QUARTER_TO_NUM.keys())}'
            )

        quarter_num = self.QUARTER_TO_NUM[quarter]
        if quarter_num < 3:
            # If the quarter is summer or fall, then the year should be incremented
            # Ex. Fall 2020 => 20212X
            year = int(year) + 1
        name = f'{year}{quarter_num}{self.CAMPUS_TO_NUM[campus]}'

        try:
            db = TinyDB(join(DB_DIR, f'merge_{name}_database.json'), access_mode='r')
        except FileNotFoundError:
            try:
                db = TinyDB(join(DB_DIR, f'sched_{name}_database.json'), access_mode='r')
            except FileNotFoundError:
                try:
                    db = TinyDB(join(DB_DIR, f'new_{name}_database.json'), access_mode='r')
                except FileNotFoundError:
                    raise FileNotFoundError

        return db

    def load_multi_db(self, campus):
        return TinyDB(join(DB_DIR, 'multi_database.json'), access_mode='r')

    def list_dbs(self, campus):
        with open(join(DB_DIR, 'metadata.json'), 'r') as file:
            metadata = json.loads(file.read())
            terms = list(metadata['terms'].keys())
            prettyTerms = []

            for term in terms:
                year = int(term[0:4])
                quarter_num = int(term[4])
                quarter = self.NUM_TO_QUARTER[quarter_num]
                term_campus = self.NUM_TO_CAMPUS[int(term[5])]

                if quarter_num < 3:
                    # If the quarter is summer or fall, then the year should be incremented
                    # Ex. Fall 2020 => 20212X
                    year -= 1

                if campus == term_campus:
                    prettyTerms.append({'year': year, 'term': quarter, 'code': term})

            return prettyTerms


fhda_campus = FHDACampus()
