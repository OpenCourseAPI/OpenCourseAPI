from collections import defaultdict

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from logger import log, log_info, log_err, log_warn
from scraper.merge import merge

def postprocess_dbs(final_db: TinyDB, term_dbs, get_term_info, load_db, campus=None):
    all_instr = {}

    for term, tags in sorted(term_dbs.items(), key=lambda item: item[0], reverse=True):
        all_instr_crns = defaultdict(set)

        if 'sched' in tags:
            db = load_db(term, 'sched', campus=campus, readonly=True)

            if 'new' in tags:
                otherdb = load_db(term, 'new', campus=campus, readonly=True)

                # Merge DBs generated by the auth and public schedule scrapers
                target = load_db(term, 'merge', campus=campus, readonly=False)

                log(term, 'magenta', 'Merging DBs...')
                merge(('auth_sched', 'public_sched'), target, otherdb, db)
            else:
                otherdb = None
                target = None

            classes = (target if target != None else db).table('classes').all()

            year, pretty_term, campus_id = get_term_info(term)

            for the_class in classes:
                if not the_class.get('times'):
                    log_warn(f'Class with CRN "{the_class.get("CRN")}" in term "{term}" does not have times!')
                    continue

                for time in the_class['times']:
                    for instructor in time['instructor']:
                        if isinstance(instructor, str) : continue

                        instructor_id = instructor.get('id')
                        instructor_pretty_id = instructor.get('pretty_id')

                        if instructor_id:
                            if not all_instr.get(instructor_id):
                                all_instr[instructor_id] = {**instructor}
                                all_instr[instructor_id]['classes'] = []

                            if the_class['CRN'] in all_instr_crns[instructor_id]:
                                continue

                            partial_class = {
                                'term_code': term,
                                'year': year,
                                'term': pretty_term,
                                'campus': campus_id,
                                'CRN': the_class['CRN'],
                                'dept': the_class['dept'],
                                'course': the_class['course'],
                                'title': the_class['title'],
                            }

                            if the_class.get('seats_taken') != None:
                                partial_class['seats_taken'] = the_class['seats_taken']

                            all_instr[instructor_id]['classes'].append(partial_class)
                            all_instr_crns[instructor_id].add(the_class['CRN'])

    final_db.drop_table('instructors')
    final_db.table('instructors').insert_multiple(all_instr.values())
