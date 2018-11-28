import django_filters

from avis.models import Structure


class StructureFilter(django_filters.FilterSet):
    class Meta:
        model = Structure
        fields = {
            'nom': ['icontains'],
            'informations': ['icontains'],
            'type': ['exact']
        }