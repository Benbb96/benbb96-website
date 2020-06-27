import django_filters

from music.models import Musique, Style


class MusiqueFilter(django_filters.FilterSet):
    has_link = django_filters.BooleanFilter(
        label='Possède des liens',
        method='search_has_link'
    )

    class Meta:
        model = Musique
        fields = {
            'titre': ['icontains'], 'artiste': ['exact'], 'styles': ['exact']
        }

    def search_has_link(self, queryset, name, value):
        return queryset.filter(liens__isnull=not value)


class StyleFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label='Nom')

    class Meta:
        model = Style
        fields = ('nom',)

