from django.urls import path

from . import views

app_name = 'my_spot'

urlpatterns = [
    path('map', views.carte, name='map'),
    path('map/tag/<str:tag_slug>', views.carte, name='tag'),
    path('spot/<slug:spot_slug>', views.spot_detail, name='spot_detail'),
    path('spot-group/<slug:spot_group_slug>', views.spot_group_detail, name='spot_group_detail')
]
