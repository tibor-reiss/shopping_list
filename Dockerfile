FROM python:3.11 as python-base

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.8.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

# Create stage for Poetry installation
FROM python-base as poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install -U pip setuptools \
	&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Create a new stage from the base python image
FROM python-base as flask-app

# Copy Poetry to app image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Copy Dependencies
COPY poetry.lock pyproject.toml ./

# Install python-dev because of psycopg2
RUN apt-get update \
    && apt-get -y install python3.11-dev
# Install Dependencies
RUN poetry install --no-interaction --no-cache --without dev

# Copy Application
COPY /src/shopping_list ./shopping_list
COPY .env .

# Run Application
EXPOSE 5000
CMD [ "poetry", "run", "flask", "--app", "./shopping_list/app/app", "run", "--host=0.0.0.0" ]
