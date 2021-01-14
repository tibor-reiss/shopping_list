from datetime import date
from flask import Blueprint, current_app, render_template, request
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField

from shopping_list.app.commands import generate_shopping_list


BP = Blueprint('list', __name__, url_prefix='')


class ShoppingListForm(FlaskForm):
    start_date = DateField('start_date', default=date.today)
    end_date = DateField('end_date', default=date.today)


@BP.route('/list', methods=['GET', 'POST'])
def view_list():
    if request.method == 'GET':
        form = ShoppingListForm()
        shopping_list = None
    elif request.method == 'POST':
        form = ShoppingListForm(request.form)
        shopping_list = generate_shopping_list(current_app.uow, form.start_date.data, form.end_date.data)
    return render_template(
        'list.html',
        form=form,
        shopping_list=shopping_list,
    )
