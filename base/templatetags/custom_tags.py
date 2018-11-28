from django import template

register = template.Library()


@register.filter
def multiply_10(value):
        return int(float(value) * 10)


@register.filter
def color(value):
    if value >= 8:
        return 'success'
    if value >= 6:
        return 'info'
    if value >= 4:
        return 'warning'
    return 'danger'
