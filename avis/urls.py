from django.urls import path

from . import views

app_name = 'avis'

urlpatterns = [
    path('', views.RecommandationIndex.as_view(), name='index'),
    path('restaurants/', views.RestaurantList.as_view(), name='restaurants')
]