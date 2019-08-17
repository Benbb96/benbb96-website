from django import forms

from tracker.models import Track, Tracker


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ('nom', 'icone', 'color')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'})
        }


class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ('commentaire',)
        widgets = {'commentaire': forms.TextInput(attrs={'placeholder': 'Facultatif', 'class': 'form-control'})}
