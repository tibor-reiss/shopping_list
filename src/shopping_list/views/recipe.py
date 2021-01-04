from flask import abort, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    FieldList,
    FloatField,
    FormField,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)

from shopping_list.app import app
from shopping_list.app.model import CATEGORIES, Recipe
from shopping_list.app.unit_of_work import add_recipe, get_recipe, get_recipes, UoW


class IngredientForm(FlaskForm):
    ing_name = StringField('ing_name')
    unit = StringField('unit')
    amount = FloatField('amount')
    category = SelectField('category', choices=CATEGORIES + [''], default='', )


class RecipeForm(FlaskForm):
    title = StringField('title', [validators.DataRequired()])
    description = TextAreaField('description')
    ingredients = FieldList(FormField(IngredientForm))


@app.route('/recipe', methods=['GET'])
def view_all_recipes():
    recipes = get_recipes(UoW())
    return render_template('recipe_all.html', recipes = recipes)


@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    if request.method == 'GET':
        recipe, ingredients = get_recipe(UoW(), recipe_id)
        if recipe is None:
            abort(404)
        ingredients.append((None, None, None))  # add an empty line to the end
        data = {'title': recipe.title, 'description': recipe.description, 'ingredients': ingredients}
        form = RecipeForm(data=data)
    elif request.method == 'POST':
        form = RecipeForm(request.form)
        recipe_title = form.data['title']
        recipe_description = form.data['description']
        _ = add_recipe(UoW(), recipe_id, recipe_title, recipe_description, form.ingredients.entries)
    return render_template('recipe_single.html', form=form, recipe_id=recipe_id)


@app.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if request.method == 'GET':
        data = {'title': None, 'description': None, 'ingredients': [(None, None, None)]}
        form = RecipeForm(data=data)
        return render_template('recipe_single.html', form=form, recipe_id='New')
    elif request.method == 'POST':
        form = RecipeForm(request.form)
        recipe_title = form.data['title']
        recipe_description = form.data['description']
        recipe_id = add_recipe(UoW(), None, recipe_title, recipe_description, form.ingredients.entries)
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
