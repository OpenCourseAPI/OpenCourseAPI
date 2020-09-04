from datetime import datetime
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.decorators import validates, pre_load, post_load

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
    # Description
    desc = fields.Str(required=True)
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
    # status = fields.Str(required=True, validate=validate.OneOf(['open', 'waitlist', 'full']))
    status = fields.Str(validate=validate.OneOf(['open', 'waitlist', 'full']))
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
        if not data.get('status') and data.get('seats') and data.get('wait_seats'):
            data['status'] = (
                'open' if data['seats'] > 0 else
                'waitlist' if data['wait_seats'] > 0 else
                'full'
            )

        return data


class ClassTimeSchema(Schema):
    days = fields.Str(required=True)
    time = fields.Str(required=True)
    room = fields.Str(required=True)
    instructor = fields.Str(required=True)
    campus = fields.Str(required=True)
    # campus = fields.Str(required=True, validate=validate.OneOf(
    #     ['FH', 'FC', 'FO', 'DA', 'DO', ''] + ['FM'] # 'FM' is only found in archived data
    # ))

    class Meta:
        ordered = True
        unknown = EXCLUDE


class InterimClassDataSchema(ClassDataSchema, ClassTimeSchema):
    pass


classDataSchema = ClassDataSchema()
classTimeSchema = ClassTimeSchema()
interimClassDataSchema = InterimClassDataSchema()
