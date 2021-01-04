import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Config:
    SECRET_CONFIG = os.environ.get('SECRET_CONFIG')
    if not SECRET_CONFIG:
        raise RuntimeError("Missing environment variable SECRET_CONFIG")
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very-difficult-to-guess-secret-key'
    DEBUG = True
    # EXPLAIN_TEMPLATE_LOADING = True


def get_postgres_connection():
    config = configparser.ConfigParser()
    config.read(Config.SECRET_CONFIG)
    host = config.get('sql_database', 'HOST', fallback=None)
    port = config.get('sql_database', 'PORT', fallback=5432)
    db = config.get('sql_database', 'DB', fallback=None)
    user = config.get('sql_database', 'USER', fallback=None)
    password = config.get('sql_database', 'PASSWORD', fallback=None)
    uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return uri


PSQL_SESSION_FACTORY = sessionmaker(bind=create_engine(get_postgres_connection()))
