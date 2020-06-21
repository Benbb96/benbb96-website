import django_filters

from music.models import Musique


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

