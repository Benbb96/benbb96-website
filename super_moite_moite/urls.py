from django.urls import path, include
from rest_framework import routers

from . import views, api_views

app_name = 'super-moite-moite'

router = routers.DefaultRouter(trailing_slash=False)
router.register('logements', api_views.LogementView)
router.register('categories', api_views.CategorieView)

urlpatterns = [
    path('', views.liste_logements, name='liste-logements'),
    path('logement/<slug>', views.LogementDetailView.as_view(), name='detail-logement'),

    path('api/', include(router.urls))
]
