from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', login_required(views.TrackerListView.as_view(), login_url='admin:login'), name='liste-tracker'),
    path('<slug:slug>', views.tracker_detail, name='detail-tracker')
]
