import datetime
import pytest
from shopping_list.app.model import Ingredient, Meal, Recipe
from shopping_list.app.repo import SqlAlchemyRepository


TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)


@pytest.fixture
def setup_repo(sqlite_session_factory):
    sqlite_repo = SqlAlchemyRepository(sqlite_session_factory())
    yield sqlite_repo


def test_add(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)
    ingredient = Ingredient('avocado', 'vegetable', 'pc')
    repo.add(ingredient)
    session.commit()
    assert session.query(Ingredient).count() == 1
    session.close()  # Needed because otherwise the next test would fail due to multiple sessions open


def test_get_existing(setup_repo, sqlite_prefill_db):
    setup_repo.session.expire_on_commit = False
    ing_from_repo = setup_repo.get(Ingredient, 'ing_name', 'feta cheese')
    assert ing_from_repo.ing_name == 'feta cheese'
    assert ing_from_repo.category == 'dairy'
    assert ing_from_repo.unit == 'g'


def test_get_non_existing(setup_repo, sqlite_prefill_db):
    ing_from_repo = setup_repo.get(Ingredient, 'ing_name', 'does_not_exist')
    assert ing_from_repo is None


def test_get_all(setup_repo, sqlite_prefill_db):
    assert len(setup_repo.get_all(Ingredient)) == 7


def test_get_all_ingredients_as_dict(setup_repo, sqlite_prefill_db):
    ing_from_repo = setup_repo.get_all_ingredients_as_dict()
    assert ing_from_repo['feta cheese'] == {'category': 'dairy', 'unit': 'g'}
    assert ing_from_repo['salt'] == {'category': 'spice', 'unit': None}


def test_get_all_recipe_ingredients(setup_repo, sqlite_prefill_db):
    recipe_id = setup_repo.get(Recipe, 'title', 'Risotto').id
    ings = setup_repo.get_all_recipe_ingredients(recipe_id)
    assert len(ings) == 5


def test_total_ingredients_multiple_meals(setup_repo, sqlite_prefill_db):
    lunch = 'Risotto'
    meal1 = Meal(TODAY, lunch=lunch, dinner=None)
    meal2 = Meal(TOMORROW, lunch=lunch, dinner=None)
    setup_repo.add(meal1)
    setup_repo.add(meal2)
    setup_repo.session.commit()
    ingredients = setup_repo.get_total_ingredients(TODAY, TOMORROW, 'lunch')
    assert len(ingredients) == 4
    for i in ingredients:
        if i[0] == 'zucchini':
            assert i == ('zucchini', 2, 'pc')


def test_total_ingredients_multiple_meals_and_dinner(setup_repo, sqlite_prefill_db):
    lunch = dinner = 'Risotto'
    meal1 = Meal(TODAY, lunch=lunch, dinner=None)
    meal2 = Meal(TOMORROW, lunch=lunch, dinner=dinner)
    setup_repo.add(meal1)
    setup_repo.add(meal2)
    setup_repo.session.commit()
    ingredients_lunch = setup_repo.get_total_ingredients(TODAY, TOMORROW, 'lunch')
    assert len(ingredients_lunch) == 4
    for i in ingredients_lunch:
        if i[0] == 'zucchini':
            assert i == ('zucchini', 2, 'pc')
    ingredients_dinner = setup_repo.get_total_ingredients(TODAY, TOMORROW, 'dinner')
    assert len(ingredients_dinner) == 4
    for i in ingredients_dinner:
        if i[0] == 'zucchini':
            assert i == ('zucchini', 1, 'pc')
