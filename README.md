## Installation
```bash
python3 -m venv <your_venv>
source <your_venv>/bin/activate
mkdir <your_shopping_list_folder>
cd <your_shopping_list_folder>
git clone git@github.com:tibor-reiss/shopping_list.git .
pip3 install .
export FLASK_APP=<your_venv>/lib/<python_version>/site-packages/shopping_list/app/app
(optional) export FLASK_ENV=development
export SECRET_CONFIG=<your_secret_config_path_and_file_name>
flask run
```
For a secret config file example see: config/secret_config_example

## Tests
Requires python3.8 and python3.9
```bash
pip3 install .[for_testing]
tox -r
```
