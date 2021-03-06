import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict


class Config:
    SECRET_CONFIG = os.environ.get('SECRET_CONFIG')
    if not SECRET_CONFIG:
        raise RuntimeError("Missing environment variable SECRET_CONFIG")
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very-difficult-to-guess-secret-key'
    MAX_CONTENT_LENGTH = 1024 * 512  # 0.5 MB
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']


def get_postgres_connection() -> str:
    config = configparser.ConfigParser()
    config.read(Config.SECRET_CONFIG)
    host = config.get('sql_database', 'HOST', fallback=None)
    port = config.get('sql_database', 'PORT', fallback=5432)
    db = config.get('sql_database', 'DB', fallback=None)
    user = config.get('sql_database', 'USER', fallback=None)
    password = config.get('sql_database', 'PASSWORD', fallback=None)
    uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return uri


def get_mongodb_connection() -> Dict[str, str]:
    config = configparser.ConfigParser()
    config.read(Config.SECRET_CONFIG)
    host = config.get('mongodb', 'HOST', fallback=None)
    port = config.get('mongodb', 'PORT', fallback=27017)
    db = config.get('mongodb', 'DB', fallback=None)
    collection = config.get('mongodb', 'COLLECTION', fallback=None)
    user = config.get('mongodb', 'USER', fallback=None)
    password = config.get('mongodb', 'PASSWORD', fallback=None)
    uri = f"mongodb://{user}:{password}@{host}:{port}/"
    return {'uri': uri, 'db': db, 'coll': collection}


def get_redis_connection() -> Dict[str, str]:
    config = configparser.ConfigParser()
    config.read(Config.SECRET_CONFIG)
    host = config.get('redis', 'HOST', fallback=None)
    port = config.get('redis', 'PORT', fallback=6379)
    password = config.get('redis', 'PASSWORD', fallback=None)
    return {'host': host, 'port': port, 'password': password}


PSQL_SESSION_FACTORY = sessionmaker(bind=create_engine(get_postgres_connection()))
MONGO_CONNECTION = get_mongodb_connection()
REDIS_CONNECTION = get_redis_connection()
