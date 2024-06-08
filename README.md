## Description
Flask-based shopping list generator.  
Recipes are stored in a postgres database (pictures in redis, which can
be switched to mongodb).  
On the main page one can enter the diet plan. List page will then generate
a shopping list for the given date range.  

## Installation
Clone the repo  
Specify env variables in .env file (sample given as .env_template)  
Build the docker image: ```docker build -t flaskapp .```  
Start the containers: ```docker compose up -d```  
From the browser: localhost:5000/index  

## Configuration
A sample redis.conf file is given in the repo because there seems to be a 
bug/feature in how docker-compose handles volumes with redis, namely without 
this file the mapped volume was not persisted on the host file system.

## One-time setup of the postgres database
```docker exec -it <name_of_container> /bin/bash```  
```psql -U postgres```  
```psql
CREATE USER sql_user WITH password 'sql_pwd';
CREATE DATABASE shlist;
GRANT ALL PRIVILEGES ON DATABASE shlist TO sql_user;
\c shlist postgres
GRANT ALL ON SCHEMA public TO sql_user;
```

## Tests
```bash
poetry install
poetry run pytest
```
