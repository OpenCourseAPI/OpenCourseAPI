from tinydb import TinyDB

from logger import log_warn, log_err


def merge_dicts(cl1, cl2, allowed):
        target = {}
        CRN = cl1.get('CRN') or 'time'

        def loop_on_keys(keys):
            for key in keys:
                if key == 'times':
                    target['times'] = []

                    times1 = cl1.pop(key)
                    times2 = cl2.pop(key)

                    if len(times1) != len(times2):
                        log_err(f'"{key}" is different for class {CRN}: "{len(times1)}" vs. "{len(times2)}"')
                        continue

                    for idx in range(len(times1)):
                        time1 = times1[idx].copy()
                        time2 = times2[idx].copy()

                        target['times'].append(merge_dicts(time1, time2, allowed=allowed))

                    continue

                val1 = cl1.pop(key, None)
                val2 = cl2.pop(key, None)

                if val1 != None and val2 != None:
                    if val1 != val2 and key not in allowed:
                        log_warn(f'"{key}" is different for class {CRN}: "{val1}" vs. "{val2}"')
                    target[key] = val1
                else:
                    target[key] = val1 if val1 != None else val2

        loop_on_keys(list(cl1.keys()))
        loop_on_keys(list(cl2.keys()))

        return target


def merge_dbs(final: TinyDB, first: TinyDB, second: TinyDB, allowed):
    classes1 = {doc['CRN']: doc for doc in first.table('classes').all()}
    classes2 = {doc['CRN']: doc for doc in second.table('classes').all()}

    classes = []

    for CRN in classes1.keys():
        cl1 = classes1[CRN].copy()
        cl2 = classes2.get(CRN)

        if cl2:
            classes.append(merge_dicts(cl1, cl2.copy(), allowed=allowed))
        else:
            log_err(f'Class {CRN} was only found in one DB!')
            classes.append(cl1)


    final.drop_tables()
    final.table('classes').insert_multiple(classes)


ALLOWED_ONE = ['title', 'instructor', 'seats', 'status', 'wait_seats', 'wait_cap']

if __name__ == '__main__':
    target = TinyDB('db/fhda/merge_202121_database.json')
    db1 = TinyDB('db/fhda/new_202121_database.json')
    # db2 = TinyDB('db/fhda/sched_202121_database.json')
    db2 = TinyDB('db/fhda/202121_database.json')

    merge_dbs(target, db1, db2, allowed=ALLOWED_ONE)
