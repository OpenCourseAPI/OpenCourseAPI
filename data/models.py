import time
import re
from datetime import datetime

from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.decorators import validates, pre_load, post_load

DAYS_PATTERN = f"^{'(M|T|W|Th|F|S|U)?'*7}$"


class ClassDataSchema(Schema):
    """
    Class Strings
    """
    # 5-digit Course Reference Number (ex. 25668)
    CRN = fields.Int(required=True)
    # Raw course string (ex. "MATH F001D.01Z")
    raw_course = fields.Str(required=True)
    # Department (ex. "CIS" or "MATH")
    dept = fields.Str(required=True)
    # Course (ex. "1A" or "31D")
    course = fields.Str(required=True)
    # Class section (ex. "01Z")
    section = fields.Str()
    # Class variant (ex. "Z")
    variant = fields.Str(validate=validate.OneOf(['', 'W', 'Z', 'Y', 'H']))

    """
    Course Info
    """
    # Course title
    title = fields.Str(required=True)
    # Class units
    units = fields.Float(required=True, min=0)

    """
    Class Dates
    """
    # Start date
    start = fields.Str(required=True)
    # End date
    end = fields.Str(required=True)

    """
    Seat info
    """
    # Class status (Open, Waitlist, Full)
    # status = fields.Str(required=True, validate=validate.OneOf(['open', 'waitlist', 'full', 'unknown']))
    status = fields.Str(validate=validate.OneOf(['open', 'waitlist', 'full', 'unknown']))
    # Number of open seats
    # seats = fields.Int(required=True, min=0)
    seats = fields.Int(min=0)
    # Number of open waitlist seats
    # wait_seats = fields.Int(required=True, min=0)
    wait_seats = fields.Int(min=0)
    # Waitlist capacity (total # of waitlist seats)
    # wait_cap = fields.Int(required=True, min=0)
    wait_cap = fields.Int(min=0)

    class Meta:
        ordered = True
        unknown = EXCLUDE

    @validates('start')
    def validate_start(self, date_str):
        self.validate_date(date_str)

    @validates('end')
    def validate_end(self, date_str):
        self.validate_date(date_str)

    def validate_date(self, date_str):
        """
        Validate the date string format
        """
        try:
            if not date_str == 'TBA':
                datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            raise ValidationError('Date must be in the format %m/%d/%Y or be "TBA".')

    @post_load
    def fix(self, data, **kwargs):
        if not data.get('status') and data.get('seats') != None and data.get('wait_seats') != None:
            data['status'] = (
                'open' if data['seats'] > 0 else
                'waitlist' if data['wait_seats'] > 0 else
                'full'
            )

        return data


class ClassTimeSchema(Schema):
    type = fields.Str()

    days = fields.Str(required=True)
    # time = fields.Str(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    instructor = fields.Str(required=True)
    location = fields.Str(required=True)
    room = fields.Str()
    campus = fields.Str()

    # campus = fields.Str(required=True, validate=validate.OneOf(
    #     ['FH', 'FC', 'FO', 'DA', 'DO', ''] + ['FM'] # 'FM' is only found in archived data
    # ))

    class Meta:
        ordered = True
        unknown = EXCLUDE

    @pre_load
    def split_time(self, data, **kwargs):
        if 'time' in data and not ('start_time' in data or 'end_time' in data):
            combo_time = data['time']
            times = ['TBA', 'TBA'] if combo_time == 'TBA' else combo_time.split('-')

            if len(times) != 2:
                raise ValidationError(
                    f"The time string '{combo_time}' has to be 'TBA' or be two times separated by a '-'",
                    field_name='start_time'
                )

            data['start_time'] = times[0].strip()
            data['end_time'] = times[1].strip()

        for key in ['start_time', 'end_time']:
            time_str = data[key]
            # Validate the time string format
            if time_str == 'TBA':
                continue
            try:
                parsed_time = time.strptime(time_str, '%I:%M %p')
            except ValueError:
                raise ValidationError('Time must be in the format %I:%M %p.', field_name=key)

            data[key] = time.strftime('%I:%M %p', parsed_time)

        return data

    @pre_load
    def fix_days(self, data, **kwargs):
        if not data['days']:
            replaced = False

            for key in ['start_time', 'time']:
                if key in data and data[key] == 'TBA':
                    data['days'] = 'TBA'
                    replaced = True
                    break

            # TODO: "unknown" instead of "TBA"
            if not replaced:
                data['days'] = 'TBA'

        return data

    @validates('days')
    def validate_days(self, days_str):
        if days_str != 'TBA' and not re.match(DAYS_PATTERN, days_str):
            raise ValidationError('Days string is not "TBA" and validation regex does not match.')

    # @validates('start_time')
    # def validate_start_time(self, date_str):
    #     self.validate_time(date_str)

    # @validates('end_time')
    # def validate_end_time(self, date_str):
    #     self.validate_time(date_str)

    # def validate_time(self, time_str):
    #     """
    #     Validate the time string format
    #     """
    #     if time_str == 'TBA':
    #         return
    #     try:
    #         time.strptime(time_str, '%I:%M %p')
    #     except ValueError:
    #         raise ValidationError('Time must be in the format %I:%M %p.')


class InterimClassDataSchema(ClassDataSchema, ClassTimeSchema):
    pass


class SeatInfoSchema(Schema):
    # 5-digit Course Reference Number (ex. 25668)
    CRN = fields.Int(required=True)

    """
    Seat info
    """
    # Class status (Open, Waitlist, Full)
    status = fields.Str(required=True, validate=validate.OneOf(['open', 'waitlist', 'full', 'unknown']))
    # Number of open seats
    seats = fields.Int(required=True, min=0)
    # Number of open waitlist seats
    wait_seats = fields.Int(required=True, min=0)
    # Waitlist capacity (total # of waitlist seats)
    wait_cap = fields.Int(required=True, min=0)

    class Meta:
        ordered = True
        unknown = EXCLUDE


classDataSchema = ClassDataSchema()
classTimeSchema = ClassTimeSchema()
interimClassDataSchema = InterimClassDataSchema()
seatInfoSchema = SeatInfoSchema()
