import uuid

from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_by', null=True)
    modified_at = models.DateTimeField(null=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='modified_by', null=True)

    class Meta:
        abstract = True


class Task(BaseModel):
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('task-detail', kwargs={'pk': self.pk})
