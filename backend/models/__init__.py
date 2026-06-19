# Importing models here ensures SQLModel metadata knows about them
from .groups import Group
from .hsc import HSC
from .hsc_student_data import HSCStudentData
from .json_dump import JsonDump
from .sslc import SSLC
from .sslc_student_data import SSLCStudentData
from .user import User

__all__ = [
    "Group",
    "JsonDump",
    "SSLC",
    "HSC",
    "SSLCStudentData",
    "HSCStudentData",
    "User",
]