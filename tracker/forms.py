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
    datetime = forms.DateTimeField(
        required=True,
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Track
        fields = ('commentaire', 'datetime')
        widgets = {
            'tracker': forms.HiddenInput(),
            'commentaire': forms.TextInput(attrs={'placeholder': 'Commentaire facultatif', 'class': 'form-control'})
        }
        labels = {'commentaire': 'Ajouter un nouveau track'}
