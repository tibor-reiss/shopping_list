from datetime import date
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField

from shopping_list.app.app import app, uow
from shopping_list.app.commands import generate_shopping_list


class ShoppingListForm(FlaskForm):
    start_date = DateField('start_date', default=date.today)
    end_date = DateField('end_date', default=date.today)


@app.route('/list', methods=['GET', 'POST'])
def view_list():
    if request.method == 'GET':
        form = ShoppingListForm()
        shopping_list = None
    elif request.method == 'POST':
        form = ShoppingListForm(request.form)
        shopping_list = generate_shopping_list(uow, form.start_date.data, form.end_date.data)
    return render_template(
        'list.html',
        form=form,
        shopping_list=shopping_list,
    )
