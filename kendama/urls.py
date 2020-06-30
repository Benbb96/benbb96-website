from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'kendama'

urlpatterns = [
    path('tricks/', views.KendamaTrickList.as_view(), name='tricks'),
    path('combos/', views.ComboList.as_view(), name='combos'),
    path('test/', TemplateView.as_view(template_name='kendama/base.html'), name='test-page'),
]
