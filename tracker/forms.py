from django import forms
from django.core.exceptions import ValidationError
from django_select2.forms import Select2MultipleWidget

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


class SelectTrackersForm(forms.Form):
    trackers = forms.ModelMultipleChoiceField(
        label='Sélectionner des trackers à comparer',
        queryset=Tracker.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trackers'].queryset = user.profil.trackers.all()

    def clean_trackers(self):
        trackers = self.cleaned_data.get('trackers')
        if len(trackers) < 2:
            raise ValidationError('Veuillez sélectionner au minimum 2 trackers.')
        return trackers
