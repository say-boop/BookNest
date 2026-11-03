class AppError(Exception):
    status_code: int | None = None
    error_code: str | None = None

    def __init__(
        self,
        message: str,
        details: str | None = None
    ):
        self.message = message
        self.details = details
