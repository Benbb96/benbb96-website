from django.contrib.sitemaps import GenericSitemap

from avis.models import Avis, Produit, Structure
from config.sitemaps import StaticViewSitemap
from music.models import Playlist, Musique

avis_dict = {
    'queryset': Avis.objects.all(),
    'date_field': 'date_creation',
}

produit_dict = {
    'queryset': Produit.objects.all(),
    'date_field': 'date_creation',
}

structure_dict = {
    'queryset': Structure.objects.all(),
    'date_field': 'date_creation',
}

palylist_dict = {
    'queryset': Playlist.objects.all(),
    'date_field': 'date_creation',
}

musique_dict = {
    'queryset': Musique.objects.all(),
    'date_field': 'date_creation',
}

sitemaps = {
    'sitemaps': {
        'static': StaticViewSitemap,
        'avis': GenericSitemap(avis_dict, priority=0.6),
        'produits': GenericSitemap(produit_dict, priority=0.4),
        'structures': GenericSitemap(structure_dict, priority=0.5),
        'playlists': GenericSitemap(palylist_dict, priority=0.5),
        'musiques': GenericSitemap(musique_dict, priority=0.4)
    }
}