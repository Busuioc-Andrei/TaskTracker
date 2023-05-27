from django import template

register = template.Library()


@register.filter(name="remove_label")
def remove_label(value):
    """Removes label from field"""
    value.label = False
    return value