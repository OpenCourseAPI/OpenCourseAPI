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


class BatchClassesSchema(Schema):
    '''
    Marshmallow Schema for a POST request to a batch endpoint for classes
    '''
    resources = fields.List(fields.Nested(ClassResourceSchema()), required=True)


batchClassesSchema = BatchClassesSchema()
