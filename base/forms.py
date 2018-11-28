from django import forms

from base.models import TestModel
from base.widgets import FirebaseUploadWidget


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ('url', )
        widgets = {'url': FirebaseUploadWidget(folder='test')}
