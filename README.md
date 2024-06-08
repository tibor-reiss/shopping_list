## Installation
Clone the repo  
Specify env variables in .env file (sample given as .env_template)  
Build the docker image: ```docker build -t flaskapp .```  
Start the containers: ```docker compose up -d```  
From the browser: localhost:5000/index  

## Tests
```bash
poetry install
poetry run pytest
```
