from os.path import join

from common import DB_DIR as ROOT_DB_DIR, CACHE_DIR as ROOT_CACHE_DIR

SSB_URL = 'https://ssb-prod.ec.wvm.edu/PROD/'
DB_DIR = join(ROOT_DB_DIR, 'wvm')
CACHE_DIR = join(ROOT_CACHE_DIR, 'wvm')

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
PREFIX_TO_CAMPUS = {v: k for k, v in CAMPUS_TO_PREFIX.items()}
