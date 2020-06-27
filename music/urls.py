from django.urls import path

from . import views

app_name = 'music'

urlpatterns = [
    path('', views.liste_musiques, name='liste-musiques'),
    path('styles', views.StyleListView.as_view(), name='liste-styles'),
    path('styles/<slug:slug>', views.StyleDetailView.as_view(), name='detail-style'),
    path('labels', views.LabelListView.as_view(), name='liste-labels'),
    path('labels/<slug:slug>', views.LabelDetailView.as_view(), name='detail-label'),
    path('playlists', views.PlaylistListView.as_view(), name='liste-playlists'),
    path('playlists/<slug:slug>', views.PlaylistDetailView.as_view(), name='detail-playlist'),
    path('artists/<slug:slug>', views.ArtisteDetailView.as_view(), name='detail-artiste'),
    path('<slug:slug_artist>/<slug:slug>-<int:pk>', views.MusiqueDetailView.as_view(), name='detail-musique'),
    path(
        'lien/<int:lien_id>/incremente_click_count',
        views.incremente_link_click_count, name='incremente_link_click_count'
    ),
    path('lien/<int:lien_id>/valider_lien', views.valider_lien, name="valider_lien")
]
