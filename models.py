from sqlalchemy import Column, Float, Boolean, Integer, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Calculation(Base):
    __tablename__ = 'calculation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    t = Column(Float, nullable=False)
    mode = Column(Boolean, nullable=False)

    __table_args__ = (
        Index('t_searcher_index', t, postgresql_using='brin'),
    )

    def __str__(self):
        return 'Calculation({0:.2f}) = {0:.2f}, {0:.2f}, {0:.2f} | Active: {mode}'.format(
            self.t, self.x, self.y, self.z, mode=self.mode,
        )
