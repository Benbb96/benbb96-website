from django.urls import path

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.TrackerListView.as_view(), name='liste-tracker'),
    path('<slug:slug>', views.TrackerDetailView.as_view(), name='detail-tracker')
]