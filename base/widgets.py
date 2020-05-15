from django import forms


class FirebaseUploadWidget(forms.TextInput):
    template_name = 'base/widgets/firebase-upload-widget.html'

    class Media:
        js = (
            'admin/js/jquery.init.js',  # In order to use django.jquery
            'https://www.gstatic.com/firebasejs/7.8.1/firebase-app.js',
            'https://www.gstatic.com/firebasejs/7.8.1/firebase-storage.js',
            'base/js/firebase-upload.js'
        )

    def __init__(self, folder, *args, **kwargs):
        super(FirebaseUploadWidget, self).__init__(*args, **kwargs)
        self.folder = folder

    def get_context(self, name, value, attrs):
        context = super(FirebaseUploadWidget, self).get_context(name, value, attrs)
        context['widget']['folder'] = self.folder
        return context
