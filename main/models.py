import uuid
from itertools import chain

from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True, editable=False)

    class Meta:
        abstract = True

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(self.__class__.__name__.lower() + '-detail', kwargs={'pk': self.pk})

    def to_dict(self):
        opts = self._meta
        data = {}
        for field in chain(opts.concrete_fields, opts.private_fields):
            data[field.name] = field.value_from_object(self)
        for field in opts.many_to_many:
            data[field.name] = [val.id for val in field.value_from_object(self)]
        return data


class Project(BaseModel):
    pass


def first_project():
    if Project:
        return Project.objects.first()
    return None


class Board(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=first_project)


class Column(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    order = models.IntegerField(null=True, editable=False)

    class Meta:
        ordering = ['order']


class Issue(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=first_project)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, editable=False)
    parent_issue = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(null=True, editable=False)

    class IssueType(models.TextChoices):
        EPIC = 'epic', _('Epic')
        USERSTORY = 'user_story', _('User Story')
        TASK = 'task', _('Task')

    issue_type = models.CharField(
        max_length=10,
        choices=IssueType.choices,
        default=IssueType.TASK
    )

    class Meta:
        ordering = ['order']


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
    pass
