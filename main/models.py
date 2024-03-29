import uuid
from datetime import timedelta
from itertools import chain

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from rules.contrib.models import RulesModel

from auth.models import User
from django.utils.translation import gettext_lazy as _

from main import rules


class BaseModel(RulesModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True,
                                   editable=False)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True,
                                    editable=False)

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

    @classmethod
    def filter_visible_items(cls, user):
        queryset = cls.objects.all()
        rule_predicate = cls._meta.rules_permissions.get("view")
        filtered_pks = [obj.pk for obj in queryset if rule_predicate(user, obj)]
        filtered_queryset = queryset.filter(pk__in=filtered_pks)
        return filtered_queryset

    class Meta:
        abstract = True


class Project(BaseModel):
    current_sprint = models.OneToOneField('Sprint', on_delete=models.SET_NULL, null=True, editable=False, related_name='current_project')

    class Meta:
        rules_permissions = {
            "view": rules.is_part_of_permission_group,
            "change": rules.is_part_of_permission_group,
            "delete": rules.is_part_of_permission_group,
        }


def first_project():
    if Project:
        return Project.objects.first()
    return None


class PermissionGroup(BaseModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='permission_group')
    members = models.ManyToManyField(User)

    def date_joined(self, member):
        invitation = Invitation.objects.get(permission_group=self, sent_to=member)
        return invitation.modified_at


class Board(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=first_project)

    @property
    def parent(self) -> Project:
        return self.project

    class Meta:
        rules_permissions = rules.parent_rules_permissions


class Column(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    order = models.IntegerField(null=True, editable=False, default=999)

    @property
    def parent(self) -> Board:
        return self.board

    class Meta:
        ordering = ['order']
        rules_permissions = rules.parent_rules_permissions


class ColorLabel(BaseModel):
    color = ColorField(default='#0000FF')

    class Meta:
        rules_permissions = {
            "view": rules.is_public,
            "change": rules.is_public,
            "delete": rules.is_public,
        }


default_issue_type_color_label_mapping = {
    'epic': 'Warning',
    'user_story': 'Success',
    'task': 'Primary'
}


class Issue(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=first_project)
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, editable=False)
    parent_issue = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='%(class)s_assigned_to', null=True, blank=True)
    color_label = models.ForeignKey(ColorLabel, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(default=now, null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(null=True, editable=False)
    in_backlog = models.BooleanField(default=True, editable=False)
    done = models.BooleanField(default=False, editable=False)

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
        if self.column and self.column.name == 'Done':
            self.done = True
        self.in_backlog = not self.done and not bool(self.column)
        self.add_default_color_label()
        super().save(*args, **kwargs)

    @property
    def parent(self) -> Project:
        return self.project

    class Meta:
        ordering = ['order']
        rules_permissions = rules.parent_rules_permissions


class Comment(BaseModel):
    name = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=5000, blank=False, null=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    @property
    def parent(self) -> Issue:
        return self.issue

    class Meta:
        rules_permissions = rules.parent_rules_permissions


class Profile(RulesModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    current_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, editable=False)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def to_dict(self):
        opts = self._meta
        data = {}
        for field in chain(opts.concrete_fields, opts.private_fields):
            data[field.name] = field.value_from_object(self)
        for field in opts.many_to_many:
            data[field.name] = [val.id for val in field.value_from_object(self)]
        return data

    class Meta:
        rules_permissions = {
            "view": rules.is_own_profile,
            "change": rules.is_own_profile,
            "delete": rules.is_own_profile,
        }


class Invitation(BaseModel):
    sent_to = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE)
    accepted = models.BooleanField(null=True, editable=False)

    class Meta:
        rules_permissions = {
            "view": rules.is_public,
            "change": rules.is_public,
        }

    @property
    def rejected(self) -> bool:
        return self.accepted is False

    @property
    def pending(self) -> bool:
        return self.accepted is None


def get_default_estimated_end_date():
    return now() + timedelta(days=14)


class Sprint(BaseModel):
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)
    estimated_end_date = models.DateTimeField(default=get_default_estimated_end_date)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, editable=False)
    index = models.PositiveIntegerField(default=1, editable=False)
    description = ''

    @property
    def parent(self) -> Project:
        return self.project

    @property
    def is_active(self) -> bool:
        return self.current_project is not None

    @property
    def days_left(self):
        if self.end_date:
            return 0
        current_date = now().date()
        days_left = (self.estimated_end_date.date() - current_date).days
        return max(days_left, 0)

    class Meta:
        rules_permissions = rules.parent_rules_permissions


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()


@receiver(post_save, sender=Project)
def create_permission_group(sender, instance, created, **kwargs):
    if created:
        PermissionGroup.objects.create(project=instance, created_by=instance.created_by,
                                       modified_by=instance.modified_by)
        instance.permission_group.members.add(instance.created_by)
