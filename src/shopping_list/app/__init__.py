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


'''TODO
  drop down menu for recipe names inside meals calendar
  autocompletion/suggestions when typing ingredients (lowercase and uppercase should not matter -> convert everything to lowercase?)
  recipe images
  more tests
  !!!jquery: get options programmatically from the previous field instead of hard-coding
  app.__init__: create bootstrap function
    should return uow?
      if yes, pass it into views
      OR: create a new class Commands/Events which require an uow -> move views functions here
  Singleton for uow.ingredients?
'''