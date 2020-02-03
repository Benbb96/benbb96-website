from django import forms
from django.contrib.auth.models import Group
from django_select2.forms import ModelSelect2MultipleWidget

from base.widgets import FirebaseUploadWidget
from my_spot.models import SpotPhoto, VISIBILITE, SpotTag


class SpotPhotoForm(forms.ModelForm):
    class Meta:
        model = SpotPhoto
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='spots')}


class PublicSpotFilterForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=SpotTag.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={
                'style': 'width: 250px',
                'data-minimum-input-length': '0',
                'data-placeholder': 'Tags'
            },
            model=SpotTag,
            search_fields=['nom__icontains'],
        ),
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
        queryset=Group.objects.none(),
        widget=ModelSelect2MultipleWidget(
            attrs={
                'style': 'width: 250px',
                'data-minimum-input-length': '0',
                'data-placeholder': 'Groupes'
            },
            model=Group,
            search_fields=['name__icontains'],
        ),
        required=False
    )
