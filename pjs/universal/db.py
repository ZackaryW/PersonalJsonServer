from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, DateTime, JSON
import datetime
from uuid import uuid4

base = declarative_base()

class log(base):
    __tablename__ = 'log'
    # hex 
    uuid = Column(String(32), primary_key=True, default=lambda: uuid4().hex)
    # timestamp
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # json
    data = Column(JSON, nullable=False)
    tags = Column(JSON, default=[], nullable=False)
    

    def jsonify(self):
        return {
            'uuid': self.uuid,
            'timestamp': self.timestamp,
            'data': self.data,
            'tags': self.tags
        }

    

