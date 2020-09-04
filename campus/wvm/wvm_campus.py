from os.path import join

from tinydb import TinyDB

from common import ApiError

from .wvm_settings import DB_DIR


class WVMCampus:
    CAMPUS = ['wv', 'mn']
    QUARTER_TO_NUM = {
        'winter': 1,
        'spring': 3,
        'summer': 5,
        'fall': 7,
    }
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


wvm_campus = WVMCampus()
