import re
from glob import glob
from os.path import join

def list_dbs(dir: str, prefix: str = '', suffix: str = '_database.json', filter = r''):
    dbs = glob(join(dir, f'{prefix}*{suffix}'))
    filtered = [db for db in dbs if re.search(filter, db)]
    return filtered
