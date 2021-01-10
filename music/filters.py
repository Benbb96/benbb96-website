import django_filters
from django.db.models import ManyToManyField, Q
from django_filters.filterset import remote_queryset
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget

from music.models import Musique, Style, Label, Artiste


class MusiqueFilter(django_filters.FilterSet):
    has_link = django_filters.BooleanFilter(
        label='Possède des liens',
        method='search_has_link'
    )

    class Meta:
        model = Musique
        fields = {
            'titre': ['icontains'],
            'artiste': ['exact'],
            'remixed_by': ['exact'],
            'featuring': ['exact'],
            'styles': ['exact']
        }
        # Utilise un widget Select2 pour les champs ManyToMany
        filter_overrides = {
            ManyToManyField: {
                'filter_class': django_filters.ModelMultipleChoiceFilter,
                'extra': lambda f: {
                    'queryset': remote_queryset(f),
                    'widget': Select2MultipleWidget(attrs={'style': 'width: 100%'})
                }
            },
        }

    def search_has_link(self, queryset, name, value):
        return queryset.filter(liens__isnull=not value)


class StyleFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label='Nom')

    class Meta:
        model = Style
        fields = ('nom',)


styles_multiple_choice_field = django_filters.ModelMultipleChoiceFilter(
    queryset=Style.objects.all(),
    widget=ModelSelect2MultipleWidget(
        queryset=Style.objects.all(),
        search_fields=['nom__icontains'],
        attrs={'class': 'form-control', 'style': 'width: 100%', 'data-minimum-input-length': 0}
    )
)


class LabelFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label='Nom')
    artistes = django_filters.ModelMultipleChoiceFilter(
        queryset=Artiste.objects.all(),
        widget=ModelSelect2MultipleWidget(
            queryset=Artiste.objects.all(),
            search_fields=['nom_artiste__icontains', 'nom__icontains', 'prenom__icontains'],
            attrs={'class': 'form-control', 'style': 'width: 100%', 'data-minimum-input-length': 0}
        )
    )
    styles = styles_multiple_choice_field

    class Meta:
        model = Label
        fields = ('nom', 'artistes')


class ArtisteFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(
        label='Texte',
        method='filter_text'
    )
    styles = styles_multiple_choice_field

    class Meta:
        model = Artiste
        fields = ('text', 'styles')

    def filter_text(self, queryset, name, value):
        return queryset.filter(
            Q(nom_artiste__icontains=value) | Q(prenom__icontains=value) |
            Q(nom__icontains=value) | Q(slug__icontains=value)
        )
