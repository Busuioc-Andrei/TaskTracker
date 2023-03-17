import uuid

from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000, blank=True)
    created_at = models.DateTimeField(null=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True, editable=False)
    modified_at = models.DateTimeField(null=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True, editable=False)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(self.__class__.__name__.lower() + '-detail', kwargs={'pk': self.pk})


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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, editable=False)
    parent_issue = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    class IssueType(models.TextChoices):
        EPIC = 'epic', _('Epic')
        USERSTORY = 'user_story', _('User Story')
        TASK = 'task', _('Task')

    issue_type = models.CharField(
        max_length=10,
        choices=IssueType.choices,
        default=IssueType.TASK
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(self.issue_type + '-detail', kwargs={'pk': self.pk})


# class Epic(Issue):
#     def __str__(self):
#         return self.name
#
#
# class UserStory(Issue):
#     parent_issue = models.ForeignKey(Epic, on_delete=models.SET_NULL, null=True)
#     start_date = models.DateTimeField(null=True)
#     end_date = models.DateTimeField(null=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Task(BaseModel):
#     # parent_issue = models.ForeignKey(Issue, on_delete=models.SET_NULL, null=True)
#     start_date = models.DateTimeField(null=True)
#     end_date = models.DateTimeField(null=True)
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         from django.urls import reverse
#         return reverse('task-detail', kwargs={'pk': self.pk})


class Comment(BaseModel):
    def __str__(self):
        return self.name
