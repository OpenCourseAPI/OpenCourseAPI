from tinydb import TinyDB, where

from common import ApiError
from campus.registry import ALL_CAMPUS


class Database:
    def load(self, campus, year, quarter):
        if campus not in ALL_CAMPUS:
            raise ApiError(
                404,
                f'Campus not found! Available campuses are {", ".join(ALL_CAMPUS.keys())}.'
            )

        return ALL_CAMPUS[campus].load_db(campus, year, quarter)

    def all_depts(self, db: TinyDB):
        return db.table('departments').all()

    def all_classes(self, db: TinyDB):
        return db.table('classes').all()

    def one_dept(self, db: TinyDB, dept: str):
        return db.table('departments').get(
            where('id') == dept
        )

    def all_classes_in_dept(self, db: TinyDB, dept: str):
        return db.table('classes').search(
            where('dept') == dept
        )

    def all_classes_in_course(self, db: TinyDB, dept: str, course: str):
        return db.table('classes').search(
            (where('dept') == dept) & (where('course') == course)
        )

    def one_class_by_crn(self, db: TinyDB, crn: int):
        courses = db.table('classes').get(
            where('CRN') == crn
        )
        return courses

    def all_courses(self, db: TinyDB):
        courses = db.table('courses').all()
        return [{k: v for k, v in course.items() if k != 'classes'} for course in courses]
        # return [{'dept': course['dept'], 'course': course['course']} for course in courses]

    def all_courses_in_dept(self, db: TinyDB, dept: str):
        return db.table('courses').search(
            where('dept') == dept
        )

    def one_course(self, db: TinyDB, dept: str, course: str):
        courses = db.table('courses').get(
            (where('dept') == dept) & (where('course') == course)
        )
        return courses


database = Database()
