from os.path import join

from common import DB_DIR as ROOT_DB_DIR, CACHE_DIR as ROOT_CACHE_DIR

SSB_URL = 'https://ssb-prod.ec.wvm.edu/PROD/'
DB_DIR = join(ROOT_DB_DIR, 'wvm')
CACHE_DIR = join(ROOT_CACHE_DIR, 'wvm')

# Year and term info
CURRENT_YEAR = 2021
CURRENT_TERM = 'winter'

# Campus term codes (West Valley & Mission)
CURRENT_TERM_CODES = {'wv': '202110', 'mc': '202110'}
