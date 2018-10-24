from django import forms

from avis.models import Avis
from base.widgets import FirebaseUploadWidget


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='avis')}