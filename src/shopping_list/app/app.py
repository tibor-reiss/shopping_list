import os

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import create_engine

from shopping_list.app.config import Config, get_postgres_connection
from shopping_list.app.model import Base
from shopping_list.app.unit_of_work import UoW


load_dotenv()


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    if test_config is None:
        app.config.from_object(Config)
        Base.metadata.create_all(create_engine(get_postgres_connection()))
        app.uow = UoW()
    else:
        app.config.from_mapping(test_config)

    from shopping_list.views import home, list, recipe
    app.register_blueprint(home.BP)
    app.register_blueprint(list.BP)
    app.register_blueprint(recipe.BP)

    return app
