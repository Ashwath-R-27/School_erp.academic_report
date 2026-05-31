from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class SslcResult(Base):
    __tablename__ = "sslc_results"

    reg_no = Column(Integer, primary_key=True)
    class_ = Column(String(1))
    first_name = Column(String(15))
    last_name = Column(String(15))
    tamil = Column(Integer)
    english = Column(Integer)
    maths = Column(Integer)
    science = Column(Integer)
    social = Column(Integer)
    total = Column(Integer)

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<SslcResult(reg_no={self.reg_no}, full_name={self.full_name}, total={self.total})>"
