```bash
pip uninstall -y shopping_list
python setup.py sdist
pip install dist/shopping_list-1.0.0.tar.gz
tox -r
export FLASK_APP=shopping_list/app
export FLASK_ENV=development
export SECRET_CONFIG=<your_secret_config_path_and_file_name>
flask run
```