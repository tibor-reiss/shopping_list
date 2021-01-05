from flask import abort, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from typing import Optional
from wtforms import (
    FieldList,
    FloatField,
    FormField,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)

from shopping_list.app import app, uow
from shopping_list.app.model import CATEGORIES
from shopping_list.app.commands import add_recipe, get_recipe, get_recipes


def validate_not_empty(field_name: Optional[str] = None):
    def _validate(form, field):
        msg = "Please select a non-empty value"
        msg += f" for '{form.data[field_name]}'!" if field_name else "!"
        if field.data == '':
            raise validators.ValidationError(msg)
    return _validate


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
        super(IngredientForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)


class RecipeForm(FlaskForm):
    title = StringField('title', [validators.DataRequired(), ])
    description = TextAreaField('description')
    ingredients = FieldList(FormField(IngredientForm))


def flash_messages(form):
    for _, e in form.errors.items():
        for i in e:
            if i:
                flash(i)


@app.route('/recipe', methods=['GET'])
def view_all_recipes():
    recipes = get_recipes(uow)
    return render_template('recipe_all.html', recipes=recipes)


@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    if request.method == 'GET':
        recipe, ingredients = get_recipe(uow, recipe_id)
        if recipe is None:
            abort(404)
        data = {'title': recipe.title, 'description': recipe.description, 'ingredients': ingredients}
        form = RecipeForm(data=data)
    elif request.method == 'POST':
        form = RecipeForm(request.form)
        form.ingredients.entries = [i for i in form.ingredients.entries if i.data['ing_name']]
        if not form.validate_on_submit():
            flash_messages(form)
        else:
            recipe_title = form.data['title']
            recipe_description = form.data['description']
            _ = add_recipe(uow, recipe_id, recipe_title, recipe_description, form.ingredients.entries)
    return render_template('recipe_single.html', form=form, recipe_id=recipe_id, ingredients=uow.ingredients)


@app.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if request.method == 'GET':
        data = {'title': None, 'description': None, 'ingredients': []}
        form = RecipeForm(data=data)
        return render_template('recipe_single.html', form=form, recipe_id='New', ingredients=uow.ingredients)
    elif request.method == 'POST':
        form = RecipeForm(request.form)
        form.ingredients.entries = [i for i in form.ingredients.entries if i.data['ing_name']]
        if not form.validate_on_submit():
            flash_messages(form)
            return render_template('recipe_single.html', form=form, recipe_id='New', ingredients=uow.ingredients)
        else:
            recipe_title = form.data['title']
            recipe_description = form.data['description']
            recipe_id = add_recipe(uow, None, recipe_title, recipe_description, form.ingredients.entries)
            return redirect(url_for('view_recipe', recipe_id=recipe_id))
