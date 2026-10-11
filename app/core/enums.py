from enum import Enum


class BookStatus(str, Enum):
    FIRST = "I will be reading"
    SECOND = "Reading"
    THIRD = "I read it"