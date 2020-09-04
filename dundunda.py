from collections import defaultdict
from tinydb import TinyDB

# db1 = TinyDB('db/fhda/new_202122_database.json')
# db2 = TinyDB('db/fhda/sched_202122_database.json')

db1 = TinyDB('db/fhda/new_202121_database.json')
db2 = TinyDB('db/fhda/sched_202121_database.json')

classes1 = {doc['CRN']: doc for doc in db1.table('classes').all()}
classes2 = {doc['CRN']: doc for doc in db2.table('classes').all()}

assert set(classes1.keys()) == set(classes2.keys())

mapping = defaultdict(set)

for CRN in classes1.keys():
    cl1 = classes1[CRN]
    cl2 = classes2[CRN]

    # del cl1['time']
    # del cl2['time']

    # inter = set(cl1.items()) ^ set(cl2.items())
    # print(inter)

    for idx, time1 in enumerate(cl1['time']):
        time2 = cl2['time'][idx]

        mapping[time2['campus']].add(time1['campus'])

        inter = set(time1.items()) ^ set(time2.items())

        # if len(inter) > 2:
        #     print(CRN, time1, '\n', time2, '\n\n')

        if ('campus', time1['campus']) in inter:
            print(CRN, time1, '\n', time2, '\n\n')

print(dict(mapping))
