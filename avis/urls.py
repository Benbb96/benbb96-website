from django.urls import path

from . import views

app_name = 'avis'

urlpatterns = [
    path('', views.AvisListView.as_view(), name='liste-avis'),
    path('<int:pk>/', views.AvisDetailView.as_view(), name='detail-avis'),
    path('restaurants/', views.RestaurantList.as_view(), name='restaurants'),
    path('restaurants/<slug:slug>/', views.RestaurantDetail.as_view(), name='restaurant')
]