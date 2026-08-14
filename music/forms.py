from django import forms
from django.urls import reverse_lazy

from base.widgets import (
    TomSelectMultipleWidget,
    TomSelectRemoteMultipleWidget,
    TomSelectRemoteWidget,
)
from music.models import Lien, LienPlaylist, Musique


class MusiqueForm(forms.ModelForm):
    class Meta:
        model = Musique
        fields = (
            "titre",
            "artiste",
            "featuring",
            "remixed_by",
            "styles",
            "album",
            "label",
            "playlists",
        )
        # Artistes (~1600) : chargement distant via l'endpoint JSON music:artiste-search.
        # Styles / playlists : petits jeux rendus côté serveur, filtrage client.
        widgets = {
            "artiste": TomSelectRemoteWidget(
                search_url=reverse_lazy("music:artiste-search"), placeholder="Artiste"
            ),
            "featuring": TomSelectRemoteMultipleWidget(
                search_url=reverse_lazy("music:artiste-search"), placeholder="Featuring"
            ),
            "remixed_by": TomSelectRemoteWidget(
                search_url=reverse_lazy("music:artiste-search"),
                placeholder="Remixé par",
            ),
            "styles": TomSelectMultipleWidget(placeholder="Styles"),
            "playlists": TomSelectMultipleWidget(placeholder="Playlists"),
        }


class BaseLienForm(forms.ModelForm):
    class Meta:
        fields = ("url", "plateforme")
        widgets = {"url": forms.TextInput(), "plateforme": forms.Select()}


class LienForm(BaseLienForm):
    class Meta(BaseLienForm.Meta):
        model = Lien


class LienPlaylistForm(BaseLienForm):
    class Meta(BaseLienForm.Meta):
        model = LienPlaylist
