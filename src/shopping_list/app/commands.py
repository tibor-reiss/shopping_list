from __future__ import annotations
from datetime import date as dt
from operator import itemgetter
import typing

from shopping_list.app.calendar import get_dates
from shopping_list.app.model import Meal, Ingredient, Recipe, RecipeIngredient
from shopping_list.app.unit_of_work import UoW

if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union
    from werkzeug.datastructures import FileStorage


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


def get_recipes(uow: UoW) -> Dict[str, int]:
    recipes = {}
    with uow:
        for r in uow.repo.get_all(Recipe):
            recipes[r.title] = r.id
    return recipes


def get_recipes_filtered_by_ings(uow: UoW, ings_to_filter: List[str]) -> Dict[str, int]:
    with uow:
        recipes = uow.repo.get_recipe_aggregated_ingredients()
        filtered_recipes = [
            (recipe.title, recipe.id) for recipe in recipes
            if all(ing in recipe.ings for ing in ings_to_filter)
        ]
    return dict(filtered_recipes)


def get_recipe(uow: UoW, id: int) -> (
        Optional[Recipe],
        Optional[List[Tuple[str, Optional[str], Optional[float], str]]],
        Optional[str]
):
    with uow:
        recipe = uow.repo.get(Recipe, 'id', id)
        if recipe is None:
            return None, None, None
        ingredients = uow.repo.get_all_recipe_ingredients(id)
        uow.session.expunge(recipe)
        img = uow.img_store.get(id)
    return recipe, ingredients, img


def add_recipe(
        uow: UoW,
        recipe_id: int,
        recipe_title: str,
        recipe_description: Optional[str],
        ingredients: List,
        img: Optional[FileStorage] = None,
) -> int:
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
            ingredient = uow.repo.get(Ingredient, 'ing_name', ing_name)
            if ingredient is None:
                ingredient = Ingredient(ing_name, category, unit)
                uow.append_ingredient(ing_name, unit, category)
            recing = RecipeIngredient(ingredient, recipe, amount)
            uow.repo.add(recing)
        uow.commit()
        recipe_id = recipe.id
        if img:
            uow.img_store.add(img, recipe_id)
        img = uow.img_store.get(recipe_id)
    return recipe_id, img


def generate_ingredient_dict(
        sh_list: List[Tuple[str, Union[int, float], str]]
) -> Dict[str, Tuple[Union[int, float], str]]:
    # Remove items with zero amount
    temp = filter(lambda x: x.total is not None, sh_list)
    temp = map(lambda x: (x[0], (x[1], x[2])), temp)
    return dict(temp)


def generate_shopping_list(uow: UoW, start_date: dt, end_date: dt) -> Dict[str, Tuple[float, str]]:
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
