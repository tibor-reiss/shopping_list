from flask import render_template, request

from shopping_list.app import app, uow
from shopping_list.app.unit_of_work import generate_shopping_list


@app.route('/list', methods=['GET', 'POST'])
def view_list():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        shopping_list = generate_shopping_list(uow, start_date, end_date)
        return render_template(
            'list.html',
            start_date = start_date,
            end_date = end_date,
            shopping_list=shopping_list,
        )
    if request.method == 'GET':
        return render_template(
            'list.html',
            start_date = None,
            end_date = None,
            shopping_list=None,
        )
