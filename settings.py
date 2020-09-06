import os

# Directory Config
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(ROOT_DIR, 'db')
CACHE_DIR = os.path.join(ROOT_DIR, 'db', '.cache')

# Year and term info
CURRENT_YEAR = 2020
CURRENT_TERM = 'fall'
