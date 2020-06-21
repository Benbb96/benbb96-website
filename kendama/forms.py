from django import forms

from base.widgets import FirebaseUploadWidget
from kendama.models import Kendama


class KendamaForm(forms.ModelForm):
    class Meta:
        model = Kendama
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='kendamas')}
