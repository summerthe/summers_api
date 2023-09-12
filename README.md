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

## API Access

The API can be access from postman, swagger or redoc.

Access postman collection from here: [Summers API Postman collection](https://www.postman.com/summersapi/workspace/my-workspace/collection/15913943-e1ec43a1-c432-47b7-a273-017647496111).

To access swagger visit `/api/v1/swagger`, and for redoc `/api/v1/redoc`.

All the public APIs can be access without any authentication, but for authenticated API the bearer authentication token is required to pass in the header.

For Swagger and redoc get the access token from `/auth/` endpoint by providing valid user's credentials and set it in `Authorize` tab.
ex. `Bearer ACCESS_TOKEN`

For postman, just like swagger get token from `/auth/` endpoint. Before doing that make sure have selected Postman environment.

After hitting the API you dont have to set token anywhere. It will be set automatically in the postman collection environment.

## Setup working env in local

### Install software dependencies

- [Mongodb](https://www.mongodb.com/try/download/community)
- Redis server

    ```sh
    sudo apt install redis-server
    ```

### To start celery queue

```sh
celery -A summers_api worker -B -l INFO -Q tube2drive_queue --concurrency=10
```

## Code safety

Register `pre-commit` hook before commiting code and also
make sure to install `requirements/local.txt`, and then run

```sh
pre-commit install
```

pre-commit ensures that your code doesn't have any syntax error,
code is formatted, and does some basic code checks before
you commit your code.

## Deployment without Docker

- Install python3.11.
- Install software dependencies.
- Clone project at `/home/ubuntu/projects/`.
- Create virtual env and install dependencies.
- Create `.env` file from `.env.example` at the same level as `.env.example`.

## Create service to startup server

- Create `/etc/systemd/system/summersapi-startup.service` file, copy
content of `docker-startup.service`(for docker) or
`startup.service`(without docker) and paste in file
you just created and then run.

    ```sh
    nano /etc/systemd/system/summersapi-startup.service
    sudo systemctl restart summersapi-startup.service
    ```

## Setup working env in local and Deployment with Docker

- Install latest version of [Docker](https://docs.docker.com/engine/install/ubuntu/)
and [docker compose](https://docs.docker.com/compose/install/linux/).
- Make sure you have created `.env` file from `.env.example`
at the same level as `.env.example`.
- Run docker compose command to create image and run containers.
For development use `docker-compose.debug.yml`.

```sh
docker compose -f docker-compose.debug.yml up
```

For deployment in production use `docker-compose.yml`.

```sh
docker compose -f docker-compose.yml up
```

## Limitation

- Tube2drive
  - For youtube channel maximum 500 videos can be download.

  - Uploaded file is stored in service account's google drive account
    and then it is shared with the user's email. This can cause service account's
    google drive account to exceed the maximum space(15Gb) and drive API can stop
    to upload further.
    Temp solution: It is required to delete old files from service account's
    drive account. To do that run `docs/Delete service account gdrive files.ipynb`
    file will delete all files. Make sure to download files before deleting.
