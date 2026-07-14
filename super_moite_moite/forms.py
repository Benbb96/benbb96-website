from django import forms
from django.core.exceptions import ValidationError

from base.widgets import TomSelectMultipleWidget
from super_moite_moite.models import Logement, Tache


class LogementForm(forms.ModelForm):
    class Meta:
        model = Logement
        fields = ("nom", "habitants")
        widgets = {
            "nom": forms.TextInput(),
            "habitants": TomSelectMultipleWidget(placeholder="Habitants"),
        }

    def __init__(self, *args, **kwargs):
        self.profil = kwargs.pop("profil", None)
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.initial = {"habitants": self.profil}

    def clean_habitants(self):
        habitants = self.cleaned_data["habitants"]
        if self.profil and self.profil not in habitants:
            raise ValidationError(
                "Vous devez vous inclure dans la liste des habitants pour avoir accès à ce logement."
            )
        return habitants


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = "__all__"
