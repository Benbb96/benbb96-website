from django.urls import path

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.TrackerListView.as_view(), name='liste-tracker'),
    path('<slug:slug>', views.tracker_detail, name='detail-tracker')
]