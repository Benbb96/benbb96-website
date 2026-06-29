import django_filters
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from base.widgets import TomSelectMultipleWidget, TomSelectRemoteMultipleWidget, TomSelectRemoteWidget
from music.models import Musique, Style, Label, Artiste, Playlist


def _artiste_remote_widget(multiple=False, placeholder=None):
    """Widget Tom Select à chargement distant pour le gros jeu « artistes »."""
    cls = TomSelectRemoteMultipleWidget if multiple else TomSelectRemoteWidget
    return cls(search_url=reverse_lazy('music:artiste-search'), placeholder=placeholder)


class MusiqueFilter(django_filters.FilterSet):
    has_link = django_filters.BooleanFilter(
        label=_('Has links'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Artistes (gros jeu) : chargement distant ; styles : rendu côté serveur.
        for name in ('artiste', 'remixed_by'):
            self._set_widget(name, _artiste_remote_widget())
        self._set_widget('featuring', _artiste_remote_widget(multiple=True))
        self._set_widget('styles', TomSelectMultipleWidget(placeholder=_('Styles')))

    def _set_widget(self, name, widget):
        field = self.filters[name].field
        field.widget = widget
        field.widget.choices = field.choices

    def search_has_link(self, queryset, name, value):
        return queryset.filter(liens__isnull=not value).distinct()


class StyleFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label=_('Name'))

    class Meta:
        model = Style
        fields = ('nom',)


def _styles_filter():
    """Filtre M2M sur les styles (petit jeu) avec Tom Select rendu côté serveur."""
    return django_filters.ModelMultipleChoiceFilter(
        queryset=Style.objects.all(),
        widget=TomSelectMultipleWidget(placeholder=_('Search via a style')),
    )


class LabelFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label=_('Name'))
    artistes = django_filters.ModelMultipleChoiceFilter(
        queryset=Artiste.objects.all(),
        widget=_artiste_remote_widget(multiple=True),
    )
    styles = _styles_filter()

    class Meta:
        model = Label
        fields = ('nom', 'artistes')


class ArtisteFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(
        label=_('Text'),
        method='search_text'
    )
    styles = _styles_filter()

    class Meta:
        model = Artiste
        fields = ('text', 'styles')

    def search_text(self, queryset, name, value):
        return queryset.filter(
            Q(nom_artiste__icontains=value) | Q(prenom__icontains=value) |
            Q(nom__icontains=value) | Q(slug__icontains=value)
        ).distinct()


class PlaylistFilter(django_filters.FilterSet):
    styles = _styles_filter()

    class Meta:
        model = Playlist
        fields = ('styles',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['styles'].method = 'filter_styles'

    def filter_styles(self, queryset, name, value):
        return queryset.filter(musiqueplaylist__musique__styles__in=value).distinct()
