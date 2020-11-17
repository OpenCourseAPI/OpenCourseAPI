from tinydb import TinyDB, where

from common import ApiError
from campus.registry import ALL_CAMPUS


class Database:
    def load(self, campus, year, quarter):
        self.validate_campus(campus)

        return ALL_CAMPUS[campus].load_db(campus, year, quarter)

    def campus_info(self, campus):
        self.validate_campus(campus)

        terms = ALL_CAMPUS[campus].list_dbs(campus)
        current_term = self.current_term(campus)

        return {'id': campus, 'current': current_term, 'terms': terms}

    def current_term(self, campus):
        self.validate_campus(campus)

        return ALL_CAMPUS[campus].get_current_term(campus)

    def validate_campus(self, campus):
        if campus not in ALL_CAMPUS:
            raise ApiError(
                404,
                f'Campus not found! Available campuses are {", ".join(ALL_CAMPUS.keys())}.'
            )

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
