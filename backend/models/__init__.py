# Importing models here ensures SQLModel metadata knows about them
from .hsc import HSC
from .hsc_student_data import HSCStudentData
from .sslc import SSLC
from .sslc_student_data import SSLCStudentData

__all__ = ["SSLC", "HSC", "SSLCStudentData", "HSCStudentData"]
