import datetime
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import DateField, FieldList, FormField, StringField

from shopping_list.app import app, uow
from shopping_list.app.commands import add_meal, get_meals


class MealForm(FlaskForm):
    date = DateField('date')
    lunch = StringField('lunch')
    dinner = StringField('dinner')


class MealListForm(FlaskForm):
    meals = FieldList(FormField(MealForm))


@app.route('/index', methods=['GET', 'POST'])
def view_index():
    if request.method == 'GET':
        meals = get_meals(uow)
        data = {'meals': meals}
        form = MealListForm(data=data)
    if request.method == 'POST':
        form = MealListForm(request.form)
        for entry in form.meals.entries:
            add_meal(uow, entry.data['date'], entry.data['lunch'], entry.data['dinner'])
    return render_template('index.html', form=form, skip=datetime.date.today().weekday())
