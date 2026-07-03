from django import forms
from django.core.exceptions import ValidationError

from base.widgets import TomSelectMultipleWidget
from tracker.models import Track, Tracker


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ('nom', 'icone', 'color', 'type')
        widgets = {
            'nom': forms.TextInput(),
            'type': forms.Select()
        }


class TrackForm(forms.ModelForm):
    valeur = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Valeur'})
    )
    datetime = forms.DateTimeField(
        required=True,
        input_formats=['%Y-%m-%dT%H:%M']
    )

    def __init__(self, *args, **kwargs):
        tracker_type = kwargs.pop('tracker_type', None)
        super().__init__(*args, **kwargs)
        if tracker_type == Tracker.TYPE_MESURE:
            self.fields['valeur'].required = True
            self.fields['valeur'].widget.attrs['required'] = 'required'

    class Meta:
        model = Track
        fields = ('valeur', 'commentaire', 'datetime')
        widgets = {
            'tracker': forms.HiddenInput(),
            'commentaire': forms.TextInput(attrs={'placeholder': 'Commentaire facultatif'})
        }
        labels = {'commentaire': 'Ajouter un nouveau track'}


class SelectTrackersForm(forms.Form):
    trackers = forms.ModelMultipleChoiceField(
        label='Sélectionner des trackers à comparer',
        queryset=Tracker.objects.all(),
        widget=TomSelectMultipleWidget(placeholder='Trackers à comparer')
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trackers'].queryset = user.profil.trackers.all()

    def clean_trackers(self):
        trackers = self.cleaned_data.get('trackers', [])
        if len(trackers) < 2:
            raise ValidationError('Veuillez sélectionner au minimum 2 trackers.')
        return trackers
