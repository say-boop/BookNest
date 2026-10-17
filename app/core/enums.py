from enum import Enum


class BookStatus(str, Enum):
    want_to_read = "want_to_read"
    reading = "reading"
    read = "read"