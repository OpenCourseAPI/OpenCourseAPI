from tinydb import TinyDB

from logger import log_warn, log_err

CONFIGS = {
    ('auth_sched', 'public_sched'): {
        'allowed': ['location', 'instructor'],
        'preference': {
            'location': 1,
            'instructor': 1
        }
    },
    ('auth_sched', 'fhda_term'): {
        'allowed': ['title', 'instructor', 'seats', 'status', 'wait_seats', 'wait_cap'],
        'preference': {}
    }
}


def merge_dicts(cl1, cl2, allowed, preference):
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

                    target['times'].append(merge_dicts(time1, time2, allowed=allowed, preference=preference))

                continue

            val1 = cl1.pop(key, None)
            val2 = cl2.pop(key, None)

            if val1 != None and val2 != None:
                if val1 != val2 and key not in allowed:
                    log_warn(f'"{key}" is different for class {CRN}: "{val1}" vs. "{val2}"')

                if preference.get(key):
                    target[key] = [val1, val2][preference[key]]
                else:
                    if val1 != val2:
                        log_warn(f'Preference not given for "{key}"')
                    target[key] = val1

            else:
                target[key] = val1 if val1 != None else val2

    loop_on_keys(list(cl1.keys()))
    loop_on_keys(list(cl2.keys()))

    return target


def merge_dbs(final: TinyDB, first: TinyDB, second: TinyDB, allowed, preference):
    classes1 = {doc['CRN']: doc for doc in first.table('classes').all()}
    classes2 = {doc['CRN']: doc for doc in second.table('classes').all()}

    classes = []

    for CRN in classes1.keys():
        cl1 = classes1[CRN].copy()
        cl2 = classes2.get(CRN)

        if cl2:
            classes.append(merge_dicts(cl1, cl2.copy(), allowed=allowed, preference=preference))
        else:
            log_err(f'Class {CRN} was only found in one DB!')
            classes.append(cl1)

    final.drop_tables()
    final.table('departments').insert_multiple(first.table('departments').all())
    final.table('courses').insert_multiple(first.table('courses').all())
    final.table('classes').insert_multiple(classes)


def merge(config_name: tuple, target: TinyDB, first: TinyDB, second: TinyDB):
    config = CONFIGS.get(config_name)
    if config:
        merge_dbs(target, first, second, config['allowed'], config['preference'])
    else:
        raise NotImplementedError
