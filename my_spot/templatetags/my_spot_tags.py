from django import template

register = template.Library()


@register.filter
def visibilite_icon(value):
    if value == 3:
        return 'eye-slash'
    if value == 2:
        return 'group'
    return 'globe'


@register.filter
def get_contrast_color(hex_color):
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

    l2 = 0.2126 * pow(r2_black_color / 255, 2.2) + 0.7152 * pow(g2_black_color / 255, 2.2) + 0.0722 * pow(b2_black_color / 255, 2.2)

    if l1 > l2:
        contrast_ratio = int((l1 + 0.05) / (l2 + 0.05))
    else:
        contrast_ratio = int((l2 + 0.05) / (l1 + 0.05))
    
    # If contrast is more than 5, return black color
    if contrast_ratio > 5:
        return '#000000'
    # if not, return white color
    return '#FFFFFF'
