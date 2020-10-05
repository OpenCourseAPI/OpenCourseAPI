from marshmallow import Schema, fields, validates_schema, ValidationError
from settings import DB_DIR, CACHE_DIR

class ApiError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status = status_code
        self.message = message


class ClassResourceSchema(Schema):
    '''
    Marshmallow Schema for a "class" resource in a batch API request
    '''
    CRN = fields.Int()
    dept = fields.Str()
    course = fields.Str()

    @validates_schema(skip_on_field_errors=True)
    def validate(self, data, *args, **kwargs):
        if not data.get('CRN') or data.get('dept'):
            raise ValidationError('At least "CRN" or "dept" have to be specified.')


class BatchClassesSchema(Schema):
    '''
    Marshmallow Schema for a POST request to a batch endpoint for classes
    '''
    resources = fields.List(fields.Nested(ClassResourceSchema()), required=True)


batchClassesSchema = BatchClassesSchema()
