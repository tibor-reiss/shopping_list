'''TODO
  drop down menu for recipe names inside meals calendar
  autocompletion/suggestions when typing ingredients (lowercase and uppercase should not matter -> convert everything to lowercase?)
  !!!jquery: get options programmatically from the previous field instead of hard-coding
  app.__init__: create bootstrap function
    should return uow?
      if yes, pass it into views
      OR: create a new class Commands/Events which require an uow -> move views functions here
  Singleton for uow.ingredients?
  shopping list + recipe ingredients: also be able to cross out stuff
      ?add JS to be able to remove rows by clicking?    

  shopping list: do not overwrite dates after rendering
'''
