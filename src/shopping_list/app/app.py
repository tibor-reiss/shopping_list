from flask import Flask
from sqlalchemy import create_engine

from shopping_list.app.config import Config, get_postgres_connection
from shopping_list.app.model import Base
from shopping_list.app.unit_of_work import UoW


app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static',
)
app.config.from_object(Config)
Base.metadata.create_all(create_engine(get_postgres_connection()))
uow = UoW()

from shopping_list.views import home, list, recipe
