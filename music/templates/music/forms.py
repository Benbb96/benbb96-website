from django import forms

from music.models import Lien


class LienForm(forms.ModelForm):
    class Meta:
        model = Lien
        fields = ('url', 'old_plateforme')
        widgets = {
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'old_plateforme': forms.Select(attrs={'class': 'form-control'})
        }
