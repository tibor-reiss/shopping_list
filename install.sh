#!/bin/bash
pip uninstall -y shopping_list
python setup.py sdist
pip install dist/shopping_list-1.0.0.tar.gz
