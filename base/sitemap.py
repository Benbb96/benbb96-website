from django.contrib.sitemaps import GenericSitemap

from avis.models import Avis, Produit, Structure
from config.sitemaps import StaticViewSitemap
from music.models import Playlist, Musique, Artiste, Style, Label

avis_dict = {
    'queryset': Avis.objects.all(),
    'date_field': 'date_edition',
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
    'date_field': 'date_modification',
}

musique_dict = {
    'queryset': Musique.objects.all(),
    'date_field': 'date_modification',
}

artiste_dict = {
    'queryset': Artiste.objects.all(),
    'date_field': 'date_modification',
}

style_dict = {
    'queryset': Style.objects.all()
}

label_dict = {
    'queryset': Label.objects.all()
}

sitemaps = {
    'sitemaps': {
        'static': StaticViewSitemap,
        'avis': GenericSitemap(avis_dict, priority=0.6),
        'produits': GenericSitemap(produit_dict, priority=0.4),
        'structures': GenericSitemap(structure_dict, priority=0.5),
        'playlists': GenericSitemap(palylist_dict, priority=0.5),
        'musiques': GenericSitemap(musique_dict, priority=0.4),
        'artistes': GenericSitemap(artiste_dict, priority=0.4),
        'styles': GenericSitemap(style_dict, priority=0.3),
        'labels': GenericSitemap(label_dict, priority=0.2),
    }
}