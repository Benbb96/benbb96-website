from django.urls import path, include
from rest_framework import routers

from . import views, api_views

app_name = 'super-moite-moite'

router = routers.DefaultRouter(trailing_slash=False)
router.register('logements', api_views.LogementView, basename='logement')
router.register('categories', api_views.CategorieView, basename='categorie')
router.register('taches', api_views.TacheView, basename='tache')
router.register('point-taches', api_views.PointTacheView, basename='point_tache')
router.register('track-taches', api_views.TrackTacheView, basename='track_tache')

urlpatterns = [
    path('', views.liste_logements, name='liste-logements'),
    path('logement/<slug>', views.LogementDetailView.as_view(), name='detail-logement'),
    path('logement/<slug>/edit', views.LogementUpdateView.as_view(), name='edition-logement'),

    path('api/', include(router.urls))
]
