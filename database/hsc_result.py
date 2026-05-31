from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from . import Base


class HSCResultBio(Base):
    __tablename__ = "hsc_result_bio"

    reg_no = Column(Integer, primary_key=True)
    class_ = Column(String(1))
    first_name = Column(String(15))
    last_name = Column(String(15))
    lang = Column(Integer)
    eng = Column(Integer)
    phy = Column(Integer)
    chem = Column(Integer)
    bio = Column(Integer)
    maths = Column(Integer)
    total = Column(Integer)
    cut_off = Column(Float)

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class HSCResultCS(Base):
    __tablename__ = "hsc_result_cs"

    reg_no = Column(Integer, primary_key=True)
    class_ = Column(String(1))
    first_name = Column(String(15))
    last_name = Column(String(15))
    lang = Column(Integer)
    eng = Column(Integer)
    phy = Column(Integer)
    chem = Column(Integer)
    csc = Column(Integer)
    maths = Column(Integer)
    total = Column(Integer)
    cut_off = Column(Float)
