from django import forms
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget

from music.models import Lien, LienPlaylist, Musique, Artiste, Style, Playlist


class MusiqueForm(forms.ModelForm):
    class Meta:
        model = Musique
        fields = ('titre', 'artiste', 'featuring', 'remixed_by', 'styles', 'album', 'label', 'playlists')
        widgets = {
            'artiste': ModelSelect2Widget(queryset=Artiste.objects.all(), search_fields=['nom_artiste__icontains']),
            'featuring': ModelSelect2MultipleWidget(
                queryset=Artiste.objects.all(), search_fields=['nom_artiste__icontains']
            ),
            'remixed_by': ModelSelect2Widget(queryset=Artiste.objects.all(), search_fields=['nom_artiste__icontains']),
            'styles': ModelSelect2MultipleWidget(
                queryset=Style.objects.all(), search_fields=['nom__startswith']
            ),
            'playlists': ModelSelect2MultipleWidget(
                queryset=Playlist.objects.all(), search_fields=['nom__icontains'],
                attrs={'data-minimum-input-length': 0}
            ),
        }


class BaseLienForm(forms.ModelForm):
    class Meta:
        fields = ('url', 'plateforme')
        widgets = {
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'plateforme': forms.Select(attrs={'class': 'form-control'})
        }


class LienForm(BaseLienForm):
    class Meta(BaseLienForm.Meta):
        model = Lien


class LienPlaylistForm(BaseLienForm):
    class Meta(BaseLienForm.Meta):
        model = LienPlaylist
