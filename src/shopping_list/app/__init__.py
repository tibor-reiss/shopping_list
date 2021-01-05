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
  unit can't be overwritten, only 1 allowed
  jquery: form.submit -> remove empty ingredient line at the end so that pop/append is not needed
  !!!jquery: get options programmatically from the previous field instead of hard-coding
  !!!order shopping_list according to category
  app.__init__: create bootstrap function
    should return uow?
      if yes, pass it into views
      OR: create a new class Commands/Events which require an uow -> move views functions here
  jquery (or in validation?): do not allow same ingredient entry twice (alert box)
  Singleton for uow.ingredients?
'''