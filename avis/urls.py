from django.urls import path

from . import views

app_name = 'avis'

urlpatterns = [
    path('', views.AvisListView.as_view(), name='liste-avis'),
    path('<int:pk>/', views.AvisDetailView.as_view(), name='detail-avis'),
    path('produits/', views.ProduitList.as_view(), name='produits'),
    path('produits/<int:pk>/', views.ProduitDetail.as_view(), name='produit'),
    path('structures/', views.StructureList.as_view(), name='structures'),
    path('structures/<slug:slug>/', views.StructureDetail.as_view(), name='structure'),
    path('categories/<slug:slug>/', views.CategorieProduitDetail.as_view(), name='categorie')
]
