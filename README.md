# Summers API

## Apps

APIs for following apps.

### User

App to manage Authentication.

### News

App to find local news, articles and subscribe newsletter.

### Tube2drive

App to download youtube playlist videos, single video or all videos from channel
and then upload to google drive.

## Setup working env

### Software dependencies

- Mongodb
- Redis server(`sudo apt install redis-server`)

### Install pre-commit

To register `pre-commit` hook before commiting code make sure to install
`requirements/local.txt`, and then run

```sh
pre-commit install
```

## To start celery queue

```sh
celery -A summers_api worker -B -l INFO -Q --concurrency=1 tube2drive_queue
```
