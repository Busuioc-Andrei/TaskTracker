import uuid
from itertools import chain

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth.models import User
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True,
                                   editable=False)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True,
                                    editable=False)

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
    order = models.IntegerField(null=True, editable=False, default=999)

    class Meta:
        ordering = ['order']


class ColorLabel(BaseModel):
    color = ColorField(default='#0000FF')


default_issue_type_color_label_mapping = {
    'epic': 'Warning',
    'user_story': 'Success',
    'task': 'Primary'
}


class Issue(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=first_project)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, editable=False)
    parent_issue = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    color_label = models.ForeignKey(ColorLabel, on_delete=models.SET_NULL, null=True, blank=True)
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

    def add_default_color_label(self):
        if not self.color_label and self.issue_type:
            issue_type_color_label_mapping = default_issue_type_color_label_mapping
            color_label_name = issue_type_color_label_mapping.get(self.issue_type)
            color_label = ColorLabel.objects.filter(name=color_label_name).first()
            if color_label:
                self.color_label = color_label

    def save(self, *args, **kwargs):
        self.add_default_color_label()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']


class Comment(BaseModel):
    name = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=5000, blank=False, null=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    current_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, editable=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
