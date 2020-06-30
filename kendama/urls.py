from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'kendama'

urlpatterns = [
    path('test', TemplateView.as_view(template_name='kendama/base.html'), name='test-page'),
]
