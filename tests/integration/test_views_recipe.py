from bs4 import BeautifulSoup
from io import BytesIO
import re
from sqlalchemy import func

from shopping_list.app.model import RecipeIngredient, Recipe, Ingredient


def get_csrf_token(client: "FlaskClient", endpoint: str):
    response = client.get(endpoint)
    return BeautifulSoup(response.data, 'lxml').find('input', id='csrf_token').get('value')


def test_recipe_get_all(sqlite_prefill_db, client):
    response = client.get('/recipe')
    assert b'RECIPES' in response.data
    parsed_response = BeautifulSoup(response.data, 'lxml')
    recipes = parsed_response.findAll('a', href=re.compile(r'^/recipe/\d'))
    assert [r.text for r in recipes] == ['Pasta with feta cheese', 'Risotto']


def test_recipe_post_all_error(sqlite_prefill_db, client):
    data = dict([
        ('search_ings', 'ricotta'),
    ])
    response = client.post('/recipe', data=data)
    assert b'The CSRF token is missing.' in response.data


def test_recipe_post_all(sqlite_prefill_db, client, mocker):
    mocker.patch('shopping_list.app.repo.func.array_agg', func.group_concat)  # array_agg is not available in sqlite
    csrf_token = get_csrf_token(client, '/recipe')
    data = dict([
        ('csrf_token', csrf_token),
        ('search_ings', 'ricotta'),
    ])
    response = client.post('/recipe', data=data)
    parsed_response = BeautifulSoup(response.data, 'lxml')
    recipes = parsed_response.findAll('a', href=re.compile(r'^/recipe/\d'))
    assert [r.text for r in recipes] == ['Risotto', ]


def test_recipe_get_one(sqlite_prefill_db, client):
    response = client.get('/recipe/1')
    parsed_response = BeautifulSoup(response.data, 'lxml')
    recipe = parsed_response.find('input', id='title')
    assert recipe.get('value') == 'Pasta with feta cheese'
    response = client.get('/recipe/2')
    parsed_response = BeautifulSoup(response.data, 'lxml')
    recipe = parsed_response.find('input', id='title')
    assert recipe.get('value') == 'Risotto'


def test_recipe_get_one_not_exist(sqlite_prefill_db, client):
    response = client.get('/recipe/3')
    assert response.status_code == 404
    assert b'Invalid recipe id.' in response.data


def test_recipe_post_one(sqlite_prefill_db, app, mocker):
    mocker.patch('shopping_list.views.recipe.validate_image', return_value=True)
    with app.uow as u:
        assert len(u.repo.get_all(RecipeIngredient)) == 5
        assert u.repo.get(Recipe, 'id', 1).title == 'Pasta with feta cheese'
    with app.test_client() as client:
        csrf_token = get_csrf_token(client, '/recipe')
        data = dict([
            ('csrf_token', csrf_token),
            ('title', 'Pasta'),
            ('ingredients-0-ing_name', 'pasta'),
            ('ingredients-0-amount', '250'),
            ('ingredients-0-unit', 'g'),
            ('ingredients-0-category', 'side_dish'),
        ])
        data['recipe_image'] = (BytesIO(b'test_image'), 'test.jpg')
        response = client.post('/recipe/1', data=data, content_type='multipart/form-data')
    parsed_response = BeautifulSoup(response.data, 'lxml')
    with app.uow as u:
        assert len(u.repo.get_all(RecipeIngredient)) == 6
        assert u.repo.get(Recipe, 'id', 1).title == 'Pasta'


def test_recipe_post_one_invalid_image(sqlite_prefill_db, app, mocker):
    with app.test_client() as client:
        csrf_token = get_csrf_token(client, '/recipe')
        data = dict([
            ('csrf_token', csrf_token),
            ('title', 'Pasta'),
            ('ingredients-0-ing_name', 'pasta'),
            ('ingredients-0-amount', '250'),
            ('ingredients-0-unit', 'g'),
            ('ingredients-0-category', 'side_dish'),
        ])
        data['recipe_image'] = (BytesIO(b'test_image'), 'test.jpg')
        response = client.post('/recipe/1', data=data, content_type='multipart/form-data')
    assert response.status_code == 404
    assert b'Invalid file format for image.' in response.data
