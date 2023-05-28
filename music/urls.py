from django.urls import path

from . import views

app_name = 'music'

urlpatterns = [
    path('', views.MusiqueListView.as_view(), name='liste-musiques'),
    path('styles', views.StyleListView.as_view(), name='liste-styles'),
    path('styles/<slug:slug>', views.StyleDetailView.as_view(), name='detail-style'),
    path('labels', views.LabelListView.as_view(), name='liste-labels'),
    path('labels/<slug:slug>', views.LabelDetailView.as_view(), name='detail-label'),
    path('playlists', views.PlaylistListView.as_view(), name='liste-playlists'),
    path('playlists/<slug:slug>', views.PlaylistDetailView.as_view(), name='detail-playlist'),
    path('create-music-from-url/', views.create_music_from_url, name='create-music-from-url'),
    path('get_music_info_from_link/', views.get_music_info_from_link, name='get_music_info_from_link'),
    path('create_artist/', views.create_artist, name='create_artist'),
    path('artists/<slug:slug>', views.ArtisteDetailView.as_view(), name='detail-artiste'),
    path('artists/', views.ArtisteListView.as_view(), name='liste-artiste'),
    path('<slug:slug_artist>/<slug:slug>-<int:pk>', views.MusiqueDetailView.as_view(), name='detail-musique'),
    path(
        'lien/<int:lien_id>/incremente_click_count',
        views.incremente_link_click_count, name='incremente_link_click_count'
    ),
    path('lien/<int:lien_id>/valider_lien', views.valider_lien, name="valider_lien"),
    path(
        'playlists/<int:playlist_id>/lien/<int:lien_id>/synchroniser_playlist',
        views.synchroniser_playlist,
        name="synchroniser_playlist"
    ),
    path('spotify_callback/', views.spotify_callback, name='spotify_callback')
]
