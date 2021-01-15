from bs4 import BeautifulSoup
from datetime import date, timedelta
import re

from shopping_list.app.commands import add_meal


def test_list_get(client):
    response = client.get('/list')
    assert b'SHOPPING LIST' in response.data


def test_list_post(sqlite_prefill_db, app):
    today = date.today()
    before = today + timedelta(days=-7)
    data = dict([
        ('start_date', before),
        ('end_date', today),
    ])
    with app.uow as u:
        add_meal(u, before, 'Risotto')
        add_meal(u, today, None, 'Risotto')
    with app.test_client() as client:
        response = client.post('/list', data=data)
        parsed_response = BeautifulSoup(response.data, 'lxml')
        names = parsed_response.findAll('input', id=re.compile(r'^ingredients-\d-ing_name'))
        amounts = parsed_response.findAll('input', id=re.compile(r'^ingredients-\d-amount'))
        units = parsed_response.findAll('input', id=re.compile(r'^ingredients-\d-unit'))
        ings = [(n.get('value'), a.get('value'), u.get('value')) for n, a, u in zip(names, amounts, units)]
        assert ings == [
            ('ricotta', '400.0', 'g'),
            ('risotto rice', '600.0', 'g'),
            ('onion', '2.0', 'pc'),
            ('zucchini', '2.0', 'pc')
        ]
