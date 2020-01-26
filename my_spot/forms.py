from django import forms

from base.widgets import FirebaseUploadWidget
from my_spot.models import SpotPhoto


class SpotPhotoForm(forms.ModelForm):
    class Meta:
        model = SpotPhoto
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='spots')}
