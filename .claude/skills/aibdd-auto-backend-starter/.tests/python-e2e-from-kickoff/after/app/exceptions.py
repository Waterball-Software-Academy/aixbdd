class BusinessError(Exception):
    def __init__(self, violation_type: str):
        self.violation_type = violation_type
        super().__init__(violation_type)


class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(message)
