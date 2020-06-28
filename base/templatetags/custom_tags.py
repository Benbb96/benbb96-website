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


@register.filter
def contrast_color(hex_color):
    """
    Util function to know if it's best to use a white or a black color on the foreground given in parameter

    :param str hex_color: the foreground color to analyse
    :return: A black or a white color
    """
    r1 = int(hex_color[1:3], 16)
    g1 = int(hex_color[3:5], 16)
    b1 = int(hex_color[5:7], 16)

    # Black RGB
    black_color = "#000000"
    r2_black_color = int(black_color[1:3], 16)
    g2_black_color = int(black_color[3:5], 16)
    b2_black_color = int(black_color[5:7], 16)

    # Calc contrast ratio
    l1 = 0.2126 * pow(r1 / 255, 2.2) + 0.7152 * pow(g1 / 255, 2.2) + 0.0722 * pow(b1 / 255, 2.2)

    l2 = 0.2126 * pow(r2_black_color / 255, 2.2) + 0.7152 * pow(g2_black_color / 255, 2.2) + 0.0722 * pow(
        b2_black_color / 255, 2.2)

    if l1 > l2:
        contrast_ratio = int((l1 + 0.05) / (l2 + 0.05))
    else:
        contrast_ratio = int((l2 + 0.05) / (l1 + 0.05))

    # If contrast is more than 5, return black color
    if contrast_ratio > 5:
        return '#000000'
    # if not, return white color
    return '#FFFFFF'
