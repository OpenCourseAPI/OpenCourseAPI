"""
Script to add seat data to DBs generated by the public schedule scraper

NOTE: this was quickly whipped up and may need cleanup
TODO: merge with fhda_scrape_term.py
"""

from os import makedirs
from os.path import join, exists

# 3rd party
from bs4 import BeautifulSoup
from tinydb import TinyDB, where
from marshmallow import Schema, fields, validate, EXCLUDE, ValidationError

from logger import log_info, log_warn, log_err
from data.models import seatInfoSchema
from .fhda_settings import DB_DIR, SSB_URL, HEADERS, CURRENT_TERM_CODES
from .fhda_scrape_term import mine

PREFIX = 'sched_'

def scrape_seats(db_dir=DB_DIR, prefix=PREFIX):
    if not exists(db_dir):
        makedirs(db_dir, exist_ok=True)

    terms = list(CURRENT_TERM_CODES.values())

    log_info(f'Started FHDA seats scraper for terms {", ".join(terms)}')

    for term in terms:
        classes = parse(mine(term))
        log_info(f'Scraped {len(classes)} classes in term {term}')

        db = TinyDB(join(db_dir, f'{PREFIX}{term}_database.json'))
        new_docs = []

        for clazz in db.table('classes'):
            CRN = clazz['CRN']

            try:
                seat_info = classes.pop(CRN)
            except KeyError:
                seat_info = {'seats': 0, 'wait_seats': 0, 'wait_cap': 0, 'status': 'unknown'}
                log_warn(f'{clazz["raw_course"]} is not included in the seat scraper data.', details={
                    'CRN': CRN
                })

            new_docs.append({**clazz, **seat_info})

        for clazz in classes.values():
            log_warn(f'CRN {clazz["CRN"]} from seat scraper data is not in the main data.')

        db.table('classes').truncate()
        db.table('classes').insert_multiple(new_docs)
        db.close()

    return terms


def parse(content):
    '''
    Parse takes the content from the request and then populates the database with the data
    :param content: (html) The html containing the courses
    :param db: (TinyDB) the current database
    '''
    soup = BeautifulSoup(content, 'html5lib')

    tables = soup.find_all('table', {'class': 'TblCourses'})
    classes = {}

    for t in tables:
        rows = t.find_all('tr', {'class': 'CourseRow'})

        for tr in rows:
            cols = tr.find_all(lambda tag: tag.name == 'td')

            if cols:
                # The first <td> is a field that is not relevant to us
                # it is either empty or contains a "flag" icon
                cols.pop(0)

                for i, c in enumerate(cols):
                    a = c.find('a')
                    cols[i] = (a.get_text() if a else cols[i].get_text()).strip()

                try:
                    data = dict(zip(HEADERS, cols))

                    if data['CRN'] in classes:
                        continue

                    data['status'] = data['status'].lower()

                    try:
                        data = seatInfoSchema.load(data)
                    except ValidationError as e:
                        log_err('Marshmallow validation failed', details={
                            'messages': e.messages,
                            'class': data
                        })
                        continue

                    classes[data['CRN']] = data

                except KeyError:
                    continue

    return classes


if __name__ == "__main__":
    scrape_seats()
