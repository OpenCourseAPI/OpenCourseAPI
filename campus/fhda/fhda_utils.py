from re import match

from .fhda_settings import COURSE_NAME_PATTERN, COURSE_TYPES_TO_FLAGS

class ValidationError(Exception):
    def __init__(self, message: str, details: str):
        super().__init__(message)

        self.message = message
        self.details = details


def clean_course_name_str(course: str):
    # Regex to clean the leading 'F'/'D' and extraneous 0's
    match_obj = match(COURSE_NAME_PATTERN, course)

    if not match_obj or not match_obj.groups():
        raise ValidationError(
            f"Whoops, the course (ex. '24A') could not be extracted from '{course}'",
            'The course name regex does not match'
        )

    if len(match_obj[0]) < 5:
        raise ValidationError(
            f"Whoops, the course (ex. '24A') could not be extracted from '{course}'",
            'The course name regex does not fully match'
        )

    # Cleaned course name, e.g. `4A`
    return match_obj[1]


def parse_course_str(raw_class: str):
    '''
    This is the key parser for the class/course strings

    String Format
    -------------
    Underlying assumptions about the format of the string:

    (dept not shown, spaces added for clarity)
    `F 01A. 01Z`
    `F 1AHL 01`

    First character   - campus ('F' or 'D')
    Next 4 characters - course name / ID with leading 0's and possibly a trailing '.'
    Last characters   - section string (1-3 chars)

    NOTE: As of Fall 2020 data, all strings are between 7-8 chars,
          and all section strings are between 2-3 chars.

    Components
    ----------
    Dept    - Department
    Course  - Course name / ID (ex. '1AL')
    Section - Class section (ex. '1HZ')
    Flags   - Extra flags from the section (ex. {'H', 'Z'})

    :param raw_class: (str) The unparsed string, ex. `C S F001A01Z`
    :return: (dict) the parsed data {'dept', 'course', 'section', 'flags'}
    '''
    # Split the raw course string by a space, to separate different parts
    # ex. 'C S F001A01Z' => ['C', 'S', 'F001A01Z']
    parts = raw_class.split(' ')

    if len(parts) < 2:
        raise ValidationError(
            f"Raw course string ('{raw_class}') is invalid",
            'At least two space separated parts could not be found'
        )

    # All parts excluding the last one are assumed to be part of the department name
    # ex. `C S` => `CS`
    dept = ''.join(parts[0:-1])
    # The last part is the actual course string (without the department)
    # ex. `F001A01Z`
    without_dept = parts[-1]

    if len(without_dept) < 6 or len(without_dept) > 8:
        raise ValidationError(
            f"Invalid course + section string ('{without_dept}')",
            'Length is not between 6-8 chars'
        )

    # First five characters are the course name
    # ex. `D001A` or `F04BH`
    course = without_dept[0:5]
    # Cleaned course name, e.g. `4A`
    cleaned_course = clean_course_name_str(course)

    # The last chars are the class section + flags
    # ex. `01Z` or `5ZH`
    section = without_dept[5:]

    # Extract flags by filtering nonalphabets from the class section string
    flags = set(filter(str.isalpha, section))

    return {
        'dept': dept,
        'course': cleaned_course,
        'section': section,
        'flags': flags,
    }


def get_class_type(campus: str, flags: set):
    '''
    From a given set of class flags, return the type of the class

    :param campus: (str) The campus (check COURSE_TYPES_TO_FLAGS)
    :param flags: (set) The flags for the class

    :return: (str) The type of class
    '''
    class_type = None

    for name, flag in COURSE_TYPES_TO_FLAGS[campus].items():
        # Exclude 'standard' because that is the fallback case
        if name != 'standard' and flag in flags:
            if class_type:
                # TODO: should this be a warning instead?
                raise ValidationError('Class has multiple types in its flags', '')
            class_type = name

    if not class_type:
        class_type = 'standard'

    return class_type
