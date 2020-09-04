from settings import DB_DIR, CACHE_DIR

class ApiError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status = status_code
        self.message = message
