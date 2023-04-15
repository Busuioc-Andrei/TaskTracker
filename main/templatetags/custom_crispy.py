from django import template

register = template.Library()


@register.filter(name="remove_label")
def remove_label(value):
    """Removes label from field"""
    value.label = False
    return value


# @register.filter(name="set_form")
# def set_form(value, form_id):
#     """Sets form of input"""
#     # value.form = form_id
#     return value
