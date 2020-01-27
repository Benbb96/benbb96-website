from django.urls import path

from . import views

app_name = 'my_spot'

urlpatterns = [
    path('map', views.carte, name="map")
]
