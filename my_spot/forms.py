from django import forms
from django.contrib.auth.models import Group

from base.widgets import TomSelectMultipleWidget
from my_spot.models import SpotPhoto, VISIBILITE, SpotTag, SpotGroup


class SpotPhotoForm(forms.ModelForm):
    class Meta:
        model = SpotPhoto
        fields = '__all__'


class PublicSpotFilterForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=SpotTag.objects.all(),
        widget=TomSelectMultipleWidget(placeholder='Tags'),
        required=False,
    )


class SpotFilterForm(PublicSpotFilterForm):
    visibilite = forms.ChoiceField(
        choices=VISIBILITE + ((0, 'Tous'),),
        initial=0,
        label='Visibilité',
        widget=forms.RadioSelect()
    )
    perso = forms.BooleanField(
        label='Seulement les miens',
        required=False
    )
    groupes = forms.ModelMultipleChoiceField(
        queryset=SpotGroup.objects.none(),
        widget=TomSelectMultipleWidget(placeholder='Groupes'),
        required=False
    )
