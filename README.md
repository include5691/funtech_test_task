# funtech_test_task
Funtech test task

## Setup

### Clone repository
```shell
git clone git@github.com:include5691/funtech_test_task.git
cd funtech_test_task
```

### Create and fulfill .env file

**Variables:**
- `SECRET_KEY`: jwt secret. You may generate it using:
```shell
openssl rand -base64 15
```
- `DATABASE_URL`: your postgres url. In this example: `postgresql+psycopg2://postgres:postgres@postgres/orders_db`
- `KAFKA_BOOTSTRAP_SERVERS`: kafka server url. In this example: `kafka:9092`
- `CELERY_BROKER_URL`: celery broker url, in this exmaple we use redis: `redis://redis:6379/0`
- `CELERY_RESULT_BACKEND`: celery result storage. In this example: `redis://redis:6379/1`
- `SLOWAPI_REDIS_URL`: requests limiter redis url. In this example: `redis://redis:6379/2`
- `FASTAPI_CACHE_REDIS_URL`: responses caching redis url. In this example: `redis://redis:6379/3`

**Copy me**:
```
SECRET_KEY="VerySecretSecret"
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres/orders_db
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
SLOWAPI_REDIS_URL=redis://redis:6379/2
FASTAPI_CACHE_REDIS_URL=redis://redis:6379/3
```

### Check your local redis, postgres and kafka servers
```shell
sudo systemctl status redis
sudo systemctl status postgresql
```
If they are active, disable them:
```shell
sudo systemctl stop redis
sudo systemctl stop postgresql
```
Check if kafka is active:
```shell
lsof -i :9092
```
If active, disable it, for example:
```shell
docker stop kafka
```

### Download, install docker and docker compose
[Install](https://docs.docker.com/engine/install/) docker engine

And docker compose plugin:
```shell
sudo apt install docker-compose-plugin
```

### Run docker copose
```shell
docker compose up --build
```

## Swagger UI
Swagger UI available after launch via url:  
http://127.0.0.1:8000/docs  