import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = [
    'flask',
    'flask-wtf',
    'psycopg2',
    'pymongo',
    'pytest-mock',
    'pytest-cov',
    'redis',
    'sqlalchemy',
]

setuptools.setup(
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
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    extras_require={'test': test_deps, },
    install_requires=[
        'wheel',
    ],
    tests_require=test_deps,
    python_requires='>=3.8',
)
