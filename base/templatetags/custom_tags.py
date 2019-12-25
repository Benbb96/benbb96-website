from urllib.parse import quote_plus

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


@register.filter
def url_quote_plus(obj):
    return quote_plus(str(obj))


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = str(v)
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
