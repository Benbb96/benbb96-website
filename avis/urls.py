from django.urls import path

from . import views

app_name = 'avis'

urlpatterns = [
    path('', views.AvisListView.as_view(), name='liste-avis'),
    path('<int:pk>/', views.AvisDetailView.as_view(), name='detail-avis'),
    path('plats/', views.PlatList.as_view(), name='plats'),
    path('plats/<int:pk>/', views.PlatDetail.as_view(), name='plat'),
    path('structures/', views.StructureList.as_view(), name='structures'),
    path('structures/<slug:slug>/', views.StructureDetail.as_view(), name='structure')
]