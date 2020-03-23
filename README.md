# SocialN-server

## Development
1. Prepare environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Set the PostgreSQL connection data as environment variables
```
export MTAA_DB_ADDR="localhost"
export MTAA_DB_PORT="5432"
export MTAA_DB_USER="postgres"
export MTAA_DB_PASS="password"
export MTAA_DB_DB="postgres"
```
3. Set Flask environment variables
```
export FLASK_APP=main.py
export FLASK_ENV=development
```
4. Run flask
```
flask run
```

## Deploy on Docker
1. Set the PostgreSQL connection data
```
# Set your enviroment variables here
export MTAA_DB_ADDR="localhost"
export MTAA_DB_PORT="5432"
export MTAA_DB_USER="postgres"
export MTAA_DB_PASS="password"
export MTAA_DB_DB="postgres"
```
2. Run `docker_start.sh` (SocialN-server runs on port 5001)

## Deploy on Docker via Jenkins


1. In `Source Code Management -> Git -> Repositories` enter URL to this Github repo
2. In `Build Triggers -> Poll SCM` enter `* * * * *`
3. In `Build -> Add build step -> Execute Shell` enter te following Command:
```
# Set your enviroment variables here
export MTAA_DB_ADDR="localhost"
export MTAA_DB_PORT="5432"
export MTAA_DB_USER="postgres"
export MTAA_DB_PASS="password"
export MTAA_DB_DB="postgres"

docker kill mtaa.docker
docker rm mtaa.docker
bash docker_start.sh
```
4. Save and run the first build (SocialN-server runs on port 5001)  
   You might have to comment temporarily the *docker kill* and *docker rm* from the previous step).
