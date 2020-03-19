from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'tracker'

router = routers.DefaultRouter(trailing_slash=False)
router.register('tracker', views.TodoView)

urlpatterns = [
    path('', views.tracker_list, name='liste-tracker'),
    path('<int:pk>/quick-add', views.tracker_quick_add, name='tracker_quick_add'),
    path('<int:pk>', views.tracker_detail, name='detail-tracker'),
    path('<int:pk>/update', views.TrackerUpdateView.as_view(), name='update-tracker'),
    path('<int:pk>/delete', views.TrackerDeleteView.as_view(), name='delete-tracker'),
    path('get-data/', views.tracker_data, name='tracker-data'),
    path('get-other-stats/', views.get_other_stats, name='tracker-other-stats'),
    path('get-history/', views.tracker_history, name='tracker-history'),
    path('track/<int:pk>/update/', views.TrackUpdateView.as_view(), name='update-track'),
    path('track/<int:pk>/delete/', views.TrackDeleteView.as_view(), name='delete-track'),

    path('api/', include(router.urls))
]
