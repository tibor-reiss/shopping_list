import os
from typing import Dict

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


class Config:
    MAX_CONTENT_LENGTH = 1024 * 512  # 0.5 MB
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']


def get_postgres_connection() -> str:
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', 5432)
    db = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PWD')
    uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return uri


def get_mongodb_connection() -> Dict[str, str]:
    host = os.getenv('MONGO_HOST', 'localhost')
    port = os.getenv('MONGO_PORT', 27017)
    db = os.getenv('MONGO_DB')
    collection = os.getenv('MONGO_COLLECTION')
    user = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASSWORD')
    uri = f"mongodb://{user}:{password}@{host}:{port}/"
    return {'uri': uri, 'db': db, 'coll': collection}


def get_redis_connection() -> Dict[str, str]:
    host = os.getenv('REDIS_HOST', 'localhost')
    port = os.getenv('REDIS_PORT', 6379)
    password = os.getenv('REDIS_PWD')
    return {'host': host, 'port': port, 'password': password}


PSQL_SESSION_FACTORY = sessionmaker(bind=create_engine(get_postgres_connection()))
MONGO_CONNECTION = get_mongodb_connection()
REDIS_CONNECTION = get_redis_connection()
