from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.tracker_list, name='liste-tracker'),
    path('<slug:slug>', views.tracker_detail, name='detail-tracker'),
    path('<slug:slug>/update', views.TrackerUpdateView.as_view(), name='update-tracker'),
    path('<slug:slug>/delete', views.TrackerDeleteView.as_view(), name='delete-tracker'),
    path('get/data/', views.tracker_data, name='tracker-data')
]
