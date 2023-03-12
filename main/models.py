import uuid

from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000)
    created_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True)
    modified_at = models.DateTimeField(null=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True)

    class Meta:
        abstract = True


class Project(BaseModel):
    def __str__(self):
        return self.name


class Board(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Column(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Issue(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Epic(Issue):
    def __str__(self):
        return self.name


class UserStory(Issue):
    parent_issue = models.ForeignKey(Epic, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class Task(Issue):
    parent_issue = models.ForeignKey(Issue, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('task-detail', kwargs={'pk': self.pk})


class Comment(BaseModel):
    def __str__(self):
        return self.name
