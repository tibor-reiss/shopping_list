from __future__ import annotations  # Needed for __enter__
from datetime import date as dt
from operator import itemgetter
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Optional, Tuple, Union

from shopping_list.app.calendar import get_dates
from shopping_list.app.config import PSQL_SESSION_FACTORY
from shopping_list.app.model import Meal, Ingredient, Recipe, RecipeIngredient
from shopping_list.app.repo import SqlAlchemyRepository


class UoW:
    def __init__(self, session_factory: sessionmaker = PSQL_SESSION_FACTORY):
        self.session_factory = session_factory
        self.ingredients = None
    
    def __enter__(self) -> UoW:
        self.session = self.session_factory()
        self.repo = SqlAlchemyRepository(self.session)
        # Initialize only the first time the uow is used (and extend it with new ingredients in add_recipe)
        if self.ingredients is None:
            self.ingredients = self.repo.get_all_ingredients()
        return self
    
    def __exit__(self, *args):
        self.session.rollback()
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def append_ingredient(self, ing_name: str, unit: Optional[str] = None, category: Optional[str] = None):
        self.ingredients[ing_name] = {'unit': unit, 'category': category}


def get_meals(uow: UoW) -> List[Meal]:
    dates = get_dates()
    meals = []
    with uow:
        for d in dates:
            meal = uow.repo.get(Meal, 'date', d) or Meal(d)
            meals.append(meal)
        uow.session.expunge_all()  # Alternative would be to keep a session open for the whole flask app
    return meals


def add_meal(uow: UoW, date: dt, lunch: Optional[str] = None, dinner: Optional[str] = None):
    with uow:
        for recipe_title in (lunch, dinner):
            if recipe_title:
                recipe = uow.repo.get(Recipe, 'title', recipe_title)
                if recipe is None:
                    recipe = Recipe(recipe_title)
                    uow.repo.add(recipe)
        meal = uow.repo.get(Meal, 'date', date) or Meal(date)
        meal.lunch = lunch
        meal.dinner = dinner
        uow.repo.add(meal)
        uow.commit()


def get_recipes(uow: UoW) -> Dict[Recipe]:
    recipes = {}
    with uow:
        for r in uow.repo.get_all(Recipe):
            recipes[r.title] = r.id
    return recipes


def get_recipe(uow: UoW, id: int) -> (Optional[Recipe], Optional[List[Tuple[str, str, float]]]):
    with uow:
        recipe = uow.repo.get(Recipe, 'id', id)
        if recipe is None:
            return None, None
        ingredients = uow.repo.get_all_recipe_ingredients(id)
        uow.session.expunge(recipe)
    return recipe, ingredients


def add_recipe(
        uow: UoW,
        recipe_id: int,
        recipe_title: str,
        recipe_description: Optional[str],
        ingredients: List) -> int:
    # TODO
    #        add JS to be able to remove rows by clicking
    with uow:
        recipe = uow.repo.get(Recipe, 'id', recipe_id)
        if recipe is None:
            recipe = Recipe(Recipe, recipe_title)
            uow.repo.add(recipe)
        recipe.title = recipe_title
        recipe.description = recipe_description
        recipe.ingredients = []  # When saving delete all existing and recreate instead of checking what is not present
        for i in ingredients:
            ing_name, unit, amount, category = itemgetter('ing_name', 'unit', 'amount', 'category')(i.data)
            if not ing_name:
                continue
            ingredient = uow.repo.get(Ingredient, 'ing_name', ing_name)
            if ingredient is None:
                ingredient = Ingredient(ing_name, category, unit)
                uow.append_ingredient(ing_name, category, unit)
            recing = RecipeIngredient(ingredient, recipe, amount)
            uow.repo.add(recing)
        uow.commit()
        recipe_id = recipe.id
    return recipe_id


def generate_ingredient_dict(sh_list: List[Tuple[str, Union[int, double], str]]) -> Dict[str, Tuple(Union[int, double], str)]:
    temp = filter(lambda x: x.total is not None, sh_list)
    temp = map(lambda x: (x[0], (x[1], x[2])), temp)
    return dict(temp)



def generate_shopping_list(uow: UoW, start_date: dt, end_date: dt) -> Dict[str, Tuple[double, str]]:
    with uow:
        ingredients_lunch = uow.repo.get_total_ingredients(start_date, end_date, 'lunch')
        ingredients_dinner = uow.repo.get_total_ingredients(start_date, end_date, 'dinner')
        ingredients = generate_ingredient_dict(ingredients_lunch)
        ingredients_dinner = generate_ingredient_dict(ingredients_dinner)
        for i in ingredients_dinner:
            if i in ingredients:
                ingredients[i] = (ingredients[i][0] + ingredients_dinner[i][0], ingredients[i][1])
            else:
                ingredients[i] = (ingredients_dinner[i][0], ingredients_dinner[i][1])
    return ingredients
