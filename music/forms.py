from django import forms

from music.models import Lien, LienPlaylist


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
