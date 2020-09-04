import os

# Directory Config
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(ROOT_DIR, 'db')
CACHE_DIR = os.path.join(ROOT_DIR, 'db', '.cache')

# Regexes
DAYS_PATTERN = f"^{'(M|T|W|Th|F|S|U)?'*7}$"
