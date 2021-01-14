from datetime import date, timedelta

from shopping_list.app.model import Meal


def test_home_get(client):
    response = client.get('/index')
    assert b'MEALS' in response.data


def test_home_post(app):
    lunch1, dinner1 = 'Chicken', 'Soup'
    lunch2, dinner2 = None, 'Salad'
    date1, date2 = date.today(), date.today() + timedelta(days=1)
    data = dict([
        ('meals-0-date', date1),
        ('meals-0-lunch', lunch1),
        ('meals-0-dinner', dinner1),
        ('meals-1-date', date2),
        ('meals-1-lunch', lunch2),
        ('meals-1-dinner', dinner2)
    ])
    with app.test_client() as client:
        response = client.post('/index', data=data)
        assert lunch1 in str(response.data)
    with app.uow as u:
        assert len(u.repo.get_all(Meal)) == 2
        meal_today = u.repo.get(Meal, 'date', date1)
        assert meal_today.date == date1
        assert meal_today.lunch == lunch1
        assert meal_today.dinner == dinner1
        meal_tomorrow = u.repo.get(Meal, 'date', date2)
        assert meal_tomorrow.date == date2
        assert meal_tomorrow.lunch == lunch2
        assert meal_tomorrow.dinner == dinner2
