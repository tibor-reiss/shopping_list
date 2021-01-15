from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = [
    'beautifulsoup4',
    'lxml',
    'pytest-mock',
    'pytest-cov',
]

setup(
    name="shopping_list",
    version="1.0.0",
    author="Tibor Reiss",
    author_email="tibor.reiss@gmail.com",
    description="Simple shopping list generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tibor-reiss/shopping_list",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    extras_require={
        'flake8': 'flake8',
        'for_testing': 'tox',
        'run_tests': test_deps,
    },
    install_requires=[
        'flask',
        'flask-wtf',
        'psycopg2',
        'pymongo',
        'redis',
        'sqlalchemy',
    ],
    python_requires='>=3.8',
)
