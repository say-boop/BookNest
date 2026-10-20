class AppError(Exception):
    status_code = None
    error_code = None
    
    def __init__(
        self, 
        message: str,
        details: str | None = None
    ):
        self.message = message
        self.details = details