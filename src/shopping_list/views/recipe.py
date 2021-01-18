from __future__ import annotations
from flask import abort, Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
import imghdr
import typing
from wtforms import (
    FieldList,
    FloatField,
    FormField,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)

from shopping_list.app.model import CATEGORIES
from shopping_list.app.commands import add_recipe, get_recipe, get_recipes, get_recipes_filtered_by_ings

if typing.TYPE_CHECKING:
    from typing import Any, Optional, Tuple
    from werkzeug.datastructures import FileStorage


BP = Blueprint('recipe', __name__, url_prefix='')


def validate_not_empty(field_name: Optional[str] = None):
    def _validate(form, field):
        msg = "Please select a non-empty value"
        msg += f" for '{form.data[field_name]}'!" if field_name else "!"
        if field.data == '':
            raise validators.ValidationError(msg)
    return _validate


def validate_search_ingredients():
    def _validate(form, field):
        try:
            field.data.split(',')
        except (AttributeError, ValueError):
            msg = 'Invalid search term for ingredients, please use a comma separated list'
            raise validators.ValidationError(msg)
    return _validate


def validate_image(img: Any) -> bool:
    if not img:
        return True
    img_header = img.read(512)
    img.seek(0)
    img_format = imghdr.what(None, img_header)
    if not img_format:
        return False
    if img_format not in current_app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return False
    return True


class SearchRecipeForm(FlaskForm):
    search_ings = StringField('search_ings', [validate_search_ingredients()])


class IngredientForm(FlaskForm):
    ing_name = StringField('ing_name')
    unit = StringField('unit')
    amount = FloatField('amount', [validators.Optional(), ])
    category = SelectField(
        'category',
        [validate_not_empty('ing_name')],
        choices=CATEGORIES + [''],
        default='',
    )

    # Needed because of FormField in RecipeForm which would require another csrf token
    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(IngredientForm, self).__init__(meta={'csrf': csrf_enabled}, *args, **kwargs)


class RecipeForm(FlaskForm):
    title = StringField('title', [validators.DataRequired(), ])
    description = TextAreaField('description')
    ingredients = FieldList(FormField(IngredientForm))


def process_request(request) -> Tuple[FileStorage, RecipeForm]:
    img = request.files['recipe_image']
    if not validate_image(img):
        abort(404, 'Invalid file format for image.')
    form = RecipeForm(request.form)
    form.ingredients.entries = [i for i in form.ingredients.entries if i.data['ing_name']]
    return img, form


def flash_messages(form):
    for _, e in form.errors.items():
        for i in e:
            if i:
                flash(i)


@BP.route('/recipe', methods=['GET', 'POST'])
def view_all_recipes():
    status_code = 200
    if request.method == 'GET':
        form = SearchRecipeForm()
        recipes = get_recipes(current_app.uow)
    elif request.method == 'POST':
        form = SearchRecipeForm(request.form)
        if not form.validate_on_submit():
            flash_messages(form)
            recipes = get_recipes(current_app.uow)
            status_code = 422
        else:
            search_ings = list(filter(lambda x: (x), map(str.strip, form.data['search_ings'].split(','))))
            if not search_ings:
                recipes = get_recipes(current_app.uow)
            else:
                recipes = get_recipes_filtered_by_ings(current_app.uow, search_ings)
    return render_template('recipe_all.html', recipes=recipes, form=form), status_code


@BP.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    status_code = 200
    if request.method == 'GET':
        recipe, ingredients, img = get_recipe(current_app.uow, recipe_id)
        if recipe is None:
            abort(404, 'Invalid recipe id.')
        data = {'title': recipe.title, 'description': recipe.description, 'ingredients': ingredients}
        form = RecipeForm(data=data)
    elif request.method == 'POST':
        img, form = process_request(request)
        if not form.validate_on_submit():
            flash_messages(form)
            _, _, img = get_recipe(current_app.uow, recipe_id)
            status_code = 422
        else:
            recipe_title = form.data['title']
            recipe_description = form.data['description']
            _, img = add_recipe(current_app.uow, recipe_id, recipe_title, recipe_description, form.ingredients.entries, img)
    return render_template(
        'recipe_single.html',
        form=form,
        recipe_id=recipe_id,
        ingredients=current_app.uow.all_ingredients,
        img=img
    ), status_code


@BP.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if request.method == 'GET':
        data = {'title': None, 'description': None, 'ingredients': []}
        form = RecipeForm(data=data)
        return render_template(
            'recipe_single.html',
            form=form,
            recipe_id='New',
            ingredients=current_app.uow.all_ingredients,
            img=None
        )
    elif request.method == 'POST':
        img, form = process_request(request)
        if not form.validate_on_submit():
            flash_messages(form)
            return render_template(
                'recipe_single.html',
                form=form,
                recipe_id='New',
                ingredients=current_app.uow.all_ingredients,
                img=None
            )
        else:
            recipe_title = form.data['title']
            recipe_description = form.data['description']
            recipe_id, _ = add_recipe(current_app.uow, None, recipe_title, recipe_description, form.ingredients.entries, img)
            return redirect(url_for('recipe.view_recipe', recipe_id=recipe_id))
