from django.urls import path

from . import views

app_name = 'music'

urlpatterns = [
    path('', views.PlaylistListView.as_view(), name='liste-playlists'),
    path('playlist/<slug:slug>', views.PlaylistDetailView.as_view(), name='detail-playlist'),
    path('<slug:slug_artist>/<slug:slug>-<int:pk>', views.MusiqueDetailView.as_view(), name='detail-musique'),
    path(
        'lien/<int:lien_id>/incremente_click_count',
        views.incremente_link_click_count, name='incremente_link_click_count'
    )
]
