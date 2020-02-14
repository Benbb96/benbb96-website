from django import template

register = template.Library()


@register.filter
def visibilite_icon(value):
    if value == 3:
        return 'eye-slash'
    if value == 2:
        return 'group'
    return 'globe'
