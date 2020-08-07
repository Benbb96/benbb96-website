from django.forms import DateField, DateInput


class MyDateField(DateField):
    def __init__(self, *, default_format='%Y-%m-%d', input_formats=None, **kwargs):
        super().__init__(**kwargs)
        self.input_formats = input_formats or [default_format]
        self.widget = DateInput(attrs={'type': 'date'}, format=default_format)
