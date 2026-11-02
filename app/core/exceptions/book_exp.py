from app.core.exceptions.base import AppError


class BookAlreadyExistsError(AppError):
    status_code = 409
    error_code = "DUPLICATE_ENTITY"


class BookNotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class BookIncorrectFileFormatImport(AppError):
    status_code = 415
    error_code = "INCORRECT_FILE_FORMAT_IMPORT"


class BookNoRequiredColumnsImport(AppError):
    status_code = 400
    error_code = "NO_REQUIRED_COLUMNS_IMPORT"
    