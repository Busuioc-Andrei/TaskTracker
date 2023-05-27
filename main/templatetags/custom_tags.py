from django import template
from main.models import Invitation

register = template.Library()


@register.filter(name="date_joined")
def date_joined(permission_group, member):
    invitation = Invitation.objects.filter(permission_group=permission_group, sent_to=member).order_by('-modified_at').first()
    if invitation:
        return invitation.modified_at
    else:
        return permission_group.created_at
