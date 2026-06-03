# Importing models here ensures SQLModel metadata knows about them
from .hsc import HSC
from .sslc import SSLC

__all__ = ["SSLC", "HSC"]
