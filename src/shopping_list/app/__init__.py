from flask import Flask


from shopping_list.app.config import Config


app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static',
)
app.config.from_object(Config)

from shopping_list.views import home, list, recipe


'''TODO
  keep list of ingredients which should not be part of shopping list (water, salt, ...) - use it in filter get_total_ingredients
  drop down menu for recipe names inside meals calendar
  autocompletion/suggestions when typing ingredients (lowercase and uppercase should not matter -> convert everything to lowercase?)
  recipe images
  more tests
  unit can't be overwritten, only 1 allowed
  jquery: form.submit -> remove empty ingredient line at the end so that pop/append is not needed
  !!!jquery: get options programmatically from the previous field instead of hard-coding
'''