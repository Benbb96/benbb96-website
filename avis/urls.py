from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'avis'

urlpatterns = [
    path('', views.AvisListView.as_view(), name='liste-avis'),
    path('<int:pk>/', views.AvisDetailView.as_view(), name='detail-avis'),
    path(_('products/'), views.ProduitList.as_view(), name='produits'),
    path(_('products/<int:pk>/'), views.ProduitDetail.as_view(), name='produit'),
    path(_('structures/'), views.StructureList.as_view(), name='structures'),
    path(_('structures/<slug:slug>/'), views.StructureDetail.as_view(), name='structure'),
    path(_('categories/<slug:slug>/'), views.CategorieProduitDetail.as_view(), name='categorie')
]
