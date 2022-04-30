from django.contrib.auth import get_user_model
from django.db import models

from apps.base.models import BaseModel

User = get_user_model()


class Newsletter(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
