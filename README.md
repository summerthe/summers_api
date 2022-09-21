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

## Setup working env in local

### Install software dependencies

- [Mongodb](https://www.mongodb.com/try/download/community)
- Redis server

    ```sh
    sudo apt install redis-server
    ```

### pre-commit

To register `pre-commit` hook before commiting code make sure to install
`requirements/local.txt`, and then run

```sh
pre-commit install
```

### To start celery queue

```sh
celery -A summers_api worker -B -l INFO -Q tube2drive_queue --concurrency=1
```

## Deployment

- Install python3.10.
- Install software dependencies.
- Clone project at `/home/ubuntu/projects/`.
- Create virtual env and install dependencies.
- Create `/etc/systemd/system/summersapi-startup.service` file, copy
content of `startup.service` and paste in newly created fiel and run.

    ```sh
    sudo systemctl restart summersapi-startup.service
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
