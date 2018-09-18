import django_filters

from avis.models import Restaurant


class RestaurantFilter(django_filters.FilterSet):
    class Meta:
        model = Restaurant
        fields = {
            'nom': ['icontains'],
            'informations': ['icontains']
        }