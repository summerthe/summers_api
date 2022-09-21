from celery import shared_task

from apps.tube2drive.utils import download_upload_single, find_videos_and_upload


@shared_task
def task_find_videos_and_upload(*args, **kwargs):
    return find_videos_and_upload(*args, **kwargs)


@shared_task
def task_download_upload_single(*args, **kwargs):
    return download_upload_single(*args, **kwargs)
