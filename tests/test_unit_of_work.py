import datetime
import pytest
from typing import Any, Optional

from shopping_list.app import commands, model
from shopping_list.app.repo import ImageStore
from shopping_list.app.unit_of_work import UoW


DINNER_NAME = 'Salad'
LUNCH_NAME = 'Chicken'
TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)


class IngredientDict():
    def __init__(self, ing_name: str, category: str, unit: Optional[str] = None, amount: Optional[float] = None):
        self.data = {
            'ing_name': ing_name,
            'unit': unit,
            'category': category,
            'amount': amount,
        }


class MockStore(ImageStore):
    def __init__(self, placeholder: Any):
        super().__init__()

    def get(self, img_id: int):
        return None

    def add(self, img: Any, img_id: int):
        pass

    def close(self):
        pass


@pytest.fixture
def uow_with_mocked_image_store(sqlite_session_factory, mocker):
    mocker.patch('shopping_list.app.unit_of_work.create_img_store', return_value=MockStore(None))
    yield UoW(sqlite_session_factory, None, None)


def add_one_meal(uow):
    with uow:
        lunch = model.Recipe(LUNCH_NAME)
        dinner = model.Recipe(DINNER_NAME)
        uow.repo.add(lunch)
        uow.repo.add(dinner)
        uow.commit()
        meal = model.Meal(TODAY, LUNCH_NAME, DINNER_NAME)
        uow.repo.add(meal)
        uow.commit()


def test_get_meals(uow_with_mocked_image_store):
    test_uow = uow_with_mocked_image_store
    add_one_meal(test_uow)
    meals = commands.get_meals(test_uow)
    assert len(meals) == 14
    assert meals[0].date == TODAY
    assert meals[0].lunch == LUNCH_NAME
    assert meals[0].dinner == DINNER_NAME


def test_add_meal(uow_with_mocked_image_store):
    test_uow = uow_with_mocked_image_store
    add_one_meal(test_uow)
    tomorrow = TODAY + datetime.timedelta(days=1)
    new_lunch, new_dinner = 'Beef', 'Soup'
    commands.add_meal(test_uow, tomorrow, new_lunch, new_dinner)
    with test_uow:
        assert test_uow.session.query(model.Meal).count() == 2
        meal = test_uow.repo.get(model.Meal, 'date', TODAY)
        assert meal.lunch == LUNCH_NAME
        assert meal.dinner == DINNER_NAME
        meal = test_uow.repo.get(model.Meal, 'date', tomorrow)
        assert meal.lunch == new_lunch
        assert meal.dinner == new_dinner


def test_get_recipes(uow_with_mocked_image_store):
    test_uow = uow_with_mocked_image_store
    add_one_meal(test_uow)
    recipes = commands.get_recipes(test_uow)
    assert len(recipes) == 2
    assert sorted(recipes.keys()) == [LUNCH_NAME, DINNER_NAME]


def test_get_recipe_existing(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    recipe, ingredients, _ = commands.get_recipe(test_uow, 2)
    assert recipe.title == 'Risotto'
    assert len(ingredients) == 5


def test_get_recipe_non_existing(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    recipe, ingredients, _ = commands.get_recipe(test_uow, 3)
    assert recipe is None
    assert ingredients is None


def test_add_recipe_new(uow_with_mocked_image_store, sqlite_prefill_db):
    recipe_id, recipe_title, recipe_description = 3, 'Pancakes', None
    ingredients = [
        IngredientDict('flour', 'side_dish', 'g', 200),
        IngredientDict('milk', 'dairy', 'ml', 400),
        IngredientDict('egg', 'other', 'pc', 2),
        IngredientDict('salt', 'spice'),
    ]
    test_uow = uow_with_mocked_image_store
    commands.add_recipe(test_uow, recipe_id, recipe_title, recipe_description, ingredients)
    with test_uow:
        recipe = test_uow.session.query(model.Recipe).filter(model.Recipe.title == 'Pancakes').one_or_none()
        assert recipe is not None
        assert len(recipe.ingredients) == 4


def test_add_recipe_existing(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    with test_uow:
        recipe = test_uow.session.query(model.Recipe).filter(model.Recipe.id == 1).one_or_none()
        assert recipe is not None
        assert recipe.title == 'Pasta with feta cheese'
        assert len(recipe.ingredients) == 0
    recipe_id, recipe_title, recipe_description = 1, 'Pasta with feta cheese and grilled sausage', None
    ingredients = [
        IngredientDict('spaghetti', 'side_dish', 'g', 300),
        IngredientDict('onion', 'vegetable', 'pc', 1),
        IngredientDict('feta cheese', 'dairy', 'g', 200),
        IngredientDict('grilled sausage', 'meat', 'pc', 2),
        IngredientDict('salt', 'spice'),
        IngredientDict('pepper', 'spice'),
    ]
    commands.add_recipe(test_uow, recipe_id, recipe_title, recipe_description, ingredients)
    with test_uow:
        recipe = test_uow.session.query(model.Recipe).filter(model.Recipe.id == 1).one_or_none()
        assert recipe is not None
        assert recipe.title == 'Pasta with feta cheese and grilled sausage'
        assert len(recipe.ingredients) == 6


def test_generate_shopping_list_one_meal(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    commands.add_meal(test_uow, TODAY, lunch='Risotto')
    shopping_list = commands.generate_shopping_list(test_uow, TODAY, TODAY)
    assert len(shopping_list) == 4
    assert shopping_list['ricotta'] == (200, 'g')


def test_generate_shopping_list_one_meal_lunch_and_dinner(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    commands.add_meal(test_uow, TODAY, lunch='Risotto', dinner='Risotto')
    shopping_list = commands.generate_shopping_list(test_uow, TODAY, TODAY)
    assert len(shopping_list) == 4
    assert shopping_list['ricotta'] == (400, 'g')


def test_generate_shopping_list_one_meal_multiple_days(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    commands.add_meal(test_uow, TODAY, lunch='Risotto', dinner='Risotto')
    commands.add_meal(test_uow, TOMORROW, lunch='Risotto', dinner='Risotto')
    shopping_list = commands.generate_shopping_list(test_uow, TODAY, TOMORROW)
    assert len(shopping_list) == 4
    assert shopping_list['ricotta'] == (800, 'g')


def test_generate_shopping_list_multiple_meals_multiple_days(uow_with_mocked_image_store, sqlite_prefill_db):
    test_uow = uow_with_mocked_image_store
    recipe_id, recipe_title, recipe_description = 3, 'Zucchini lasagne', None
    ingredients = [
        IngredientDict('lasagne', 'side_dish', 'g', 200),
        IngredientDict('onion', 'vegetable', 'pc', 2),
        IngredientDict('zucchini', 'vegetable', 'pc', 2),
        IngredientDict('ricotta', 'dairy', 'g', 100),
        IngredientDict('salt', 'spice'),
        IngredientDict('pepper', 'spice'),
    ]
    commands.add_recipe(test_uow, recipe_id, recipe_title, recipe_description, ingredients)
    commands.add_meal(test_uow, TODAY, lunch='Risotto', dinner='Zucchini lasagne')
    commands.add_meal(test_uow, TOMORROW, lunch='Risotto')
    shopping_list = commands.generate_shopping_list(test_uow, TODAY, TOMORROW)
    assert len(shopping_list) == 5
    assert shopping_list['ricotta'] == (500, 'g')
