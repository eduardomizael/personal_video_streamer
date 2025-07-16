from django.db import models
from apps.base.models import BaseModel


class Video(BaseModel):
    title = models.CharField(max_length=200)
    duration = models.PositiveIntegerField()
    hash = models.CharField(max_length=32)
    path = models.CharField(max_length=256)
    thumbnail = models.CharField(max_length=256)

    def __str__(self):
        return self.title