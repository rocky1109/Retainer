
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base


class App(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    state = Column(Integer)
    error = Column(String, default='')
    error_log = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, name=None, state=None):
        self.name = name
        self.state = state

    def __repr__(self):
        return '<App {0}>'.format(self.name)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'error': self.error,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
