from django import forms

from base.widgets import FirebaseUploadWidget
from super_moite_moite.models import Tache


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='taches')}
