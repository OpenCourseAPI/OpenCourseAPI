from functools import wraps

from flask import Flask, jsonify, request, render_template, send_from_directory

from data.access import ApiError, database
from settings import CURRENT_YEAR, CURRENT_TERM


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


# Flask config
application = Flask(
    __name__,
    # template_folder='frontend/templates',
    # static_folder='frontend/static'
)
application.config['JSON_SORT_KEYS'] = False
application.url_map.strict_slashes = False
application.after_request(add_cors_headers)


# @application.route('/docs/<path:filename>')
# def static_docs(filename):
#     return send_from_directory('docs', filename)


# @application.route('/')
# def idx():
#     return render_template('index.html')


def campus_api(path: str, methods=None):
    def decorator(func):
        @application.route(f'/<campus>/{path}', methods=(methods or ['GET']))
        @wraps(func)
        def api(campus, *args, **kwargs):
            year = request.args.get('year') or CURRENT_YEAR
            quarter = request.args.get('quarter') or CURRENT_TERM

            try:
                try:
                    db = database.load(campus, year, quarter)
                    ret = func(db, *args, **kwargs)
                except FileNotFoundError:
                    raise ApiError(
                        404,
                        'Data for requested campus, year, and quarter combo does not exist.'
                    )

                if ret is None or (isinstance(ret, list) and len(ret) == 0):
                    raise ApiError(404, 'No results')

            except ApiError as e:
                return jsonify({'error': e.message}), e.status

            return jsonify(ret), 200

        return api
    return decorator


def campus_multi_term_api(path: str, methods=None):
    def decorator(func):
        @application.route(f'/<campus>/{path}', methods=(methods or ['GET']))
        @wraps(func)
        def api(campus, *args, **kwargs):
            try:
                try:
                    db = database.load_multi_db(campus)
                    ret = func(db, *args, **kwargs)
                except FileNotFoundError:
                    raise ApiError(
                        404,
                        'Data for requested campus does not exist.'
                    )

                if ret is None or (isinstance(ret, list) and len(ret) == 0):
                    raise ApiError(404, 'No results')

            except ApiError as e:
                return jsonify({'error': e.message}), e.status

            return jsonify(ret), 200

        return api
    return decorator


@application.route('/<campus>')
def api_campus(campus):
    try:
        ret = database.campus_info(campus)
    except ApiError as e:
        return jsonify({'error': e.message}), e.status

    return jsonify(ret), 200


@campus_multi_term_api('instructors/<instructor>')
def api_one_instructor(db, instructor):
    return database.one_instructor(db, instructor)


@campus_api('courses')
def api_courses(db):
    return database.all_courses(db)


@campus_api('classes')
def api_classes(db):
    return database.all_classes(db)


@campus_api('classes/<crn>')
def api_classes_by_crn(db, crn):
    return database.one_class_by_crn(db, int(crn))


@campus_api('depts')
def api_depts(db):
    return database.all_depts(db)


@campus_api('depts/<dept>')
def api_dept(db, dept):
    return database.one_dept(db, dept)


@campus_api('depts/<dept>/classes')
def api_dept_classes(db, dept):
    return database.all_classes_in_dept(db, dept)


@campus_api('depts/<dept>/courses')
def api_dept_courses(db, dept):
    return database.all_courses_in_dept(db, dept)


@campus_api('depts/<dept>/courses/<course>')
def api_dept_course(db, dept, course):
    return database.one_course(db, dept, course)


@campus_api('depts/<dept>/courses/<course>/classes')
def api_dept_course_classes(db, dept, course):
    return database.all_classes_in_course(db, dept, course)


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
