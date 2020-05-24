from django import forms
from django.core.exceptions import ValidationError
from django_select2.forms import ModelSelect2MultipleWidget

from base.models import Profil
from base.widgets import FirebaseUploadWidget
from super_moite_moite.models import Tache, Logement


class LogementForm(forms.ModelForm):
    class Meta:
        model = Logement
        fields = ('nom', 'habitants')
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'habitants': ModelSelect2MultipleWidget(
                model=Profil,
                search_fields=[
                    'user__username__icontains',
                    'user__first_name__icontains',
                    'user__last_name__icontains',
                    'user__email__icontains'
                ]
            )
        }

    def __init__(self, *args, **kwargs):
        self.profil = kwargs.pop('profil', None)
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.initial = {'habitants': self.profil}

    def clean_habitants(self):
        habitants = self.cleaned_data['habitants']
        if self.profil and self.profil not in habitants:
            raise ValidationError(
                'Vous devez vous inclure dans la liste des habitants pour avoir accès à ce logement.'
            )
        return habitants


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='taches')}
