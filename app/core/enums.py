from enum import Enum


class BookStatus(str, Enum):
    want_to_read = "I will be reading"
    reading = "Reading"
    read = "I read it"