
import json

with open("settings.json") as fh:
    settings = json.load(fh)

    if not settings.has_key("SQL_DB_PATH"):
        settings["SQL_DB_PATH"] = "sqlite:///apps.sqlite3"


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(settings["SQL_DB_PATH"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from models import App
    Base.metadata.create_all(bind=engine)
