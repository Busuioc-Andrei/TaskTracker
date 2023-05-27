import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from rules.contrib.models import RulesModelMixin, RulesModelBase

from main import rules


class User(RulesModelMixin, AbstractUser, metaclass=RulesModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        rules_permissions = {
            "view": rules.is_public,
            "change": rules.is_public,
            "delete": rules.is_public,
        }
