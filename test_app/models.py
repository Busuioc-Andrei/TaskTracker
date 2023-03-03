import uuid

from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    modified_at = models.DateTimeField()
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class Task(BaseModel):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
