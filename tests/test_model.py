from datetime import date
import pytest
from sqlalchemy.exc import IntegrityError

from shopping_list.app import model


def test_add_new_recipe(sqlite_session_factory):
    session = sqlite_session_factory()
    recipe = model.Recipe('Chicken with potatos')
    session.add(recipe)
    session.commit()
    assert session.query(model.Recipe).count() == 1


def test_add_new_meal_throws_error(sqlite_session_factory):
    session = sqlite_session_factory()
    meal = model.Meal(date.today(), 'Chicken')
    session.add(meal)
    with pytest.raises(IntegrityError):
        session.commit()


def test_add_new_meal_with_recipes(sqlite_session_factory):
    lunch, dinner = 'Chicken', 'Beef'
    meal = model.Meal(date.today(), lunch, dinner)
    recipe1 = model.Recipe(lunch)
    recipe2 = model.Recipe(dinner)
    session = sqlite_session_factory()
    session.add_all([recipe1, recipe2])
    session.commit()
    session.add(meal)
    session.commit()
    assert session.query(model.Recipe).count() == 2
    assert session.query(model.Meal).count() == 1


def test_add_new_recipe_with_ingredient(sqlite_session_factory):
    recipe = model.Recipe('Chicken')
    ingredient = model.Ingredient('salt', 'spice')
    recipe.ingredients.append(ingredient)
    session = sqlite_session_factory()
    session.add_all([recipe, ingredient])
    session.commit()
    assert session.query(model.Recipe).count() == 1
    assert session.query(model.Ingredient).count() == 1
    assert session.query(model.RecipeIngredient).count() == 1
