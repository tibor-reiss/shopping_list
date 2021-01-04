import datetime
import pytest
from sqlalchemy.orm import sessionmaker

from shopping_list.app import model, unit_of_work


DINNER_NAME = 'Salad'
LUNCH_NAME = 'Chicken'
TODAY = datetime.date.today()


class UoWSqlite(unit_of_work.UoW):
    def __init__(self, session_factory: sessionmaker):
        print('***test uow')
        self.session_factory = session_factory


@pytest.fixture
def add_one_meal(sqlite_session_factory):
    with UoWSqlite(sqlite_session_factory) as uow:
        lunch = model.Recipe(LUNCH_NAME)
        dinner = model.Recipe(DINNER_NAME)
        uow.repo.add(lunch)
        uow.repo.add(dinner)
        uow.commit()
        meal = model.Meal(TODAY, LUNCH_NAME, DINNER_NAME)
        uow.repo.add(meal)
        uow.commit()


def test_get_meals(sqlite_session_factory, add_one_meal):
    test_uow = UoWSqlite(sqlite_session_factory)
    meals = unit_of_work.get_meals(test_uow)
    assert len(meals) == 14
    assert meals[0].date == TODAY
    assert meals[0].lunch == LUNCH_NAME
    assert meals[0].dinner == DINNER_NAME


def test_add_meal(sqlite_session_factory, add_one_meal):
    test_uow = UoWSqlite(sqlite_session_factory)
    tomorrow = TODAY + datetime.timedelta(days=1)
    new_lunch, new_dinner = 'Beef', 'Soup'
    unit_of_work.add_meal(test_uow, tomorrow, new_lunch, new_dinner)
    with test_uow:
        assert test_uow.session.query(model.Meal).count() == 2
        meal = test_uow.repo.get(model.Meal, 'date', TODAY)
        assert meal.lunch == LUNCH_NAME
        assert meal.dinner == DINNER_NAME
        meal = test_uow.repo.get(model.Meal, 'date', tomorrow)
        assert meal.lunch == new_lunch
        assert meal.dinner == new_dinner
