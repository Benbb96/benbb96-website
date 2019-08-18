import random

import soundcloud
from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

from base.models import Profil


class Pays(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Pays'

    def __str__(self):
        return self.nom


class Style(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return self.nom


class Playlist(models.Model):
    nom = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    createur = models.ForeignKey(Profil, related_name='playlists_crees', on_delete=models.CASCADE)
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    date_modification = models.DateTimeField('dernière modification', auto_now=True)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('music:detail-playlist', kwargs={'slug': self.slug})

    def styles(self):
        return Style.objects.filter(musiques__musiqueplaylist__playlist=self).distinct()

    def artistes(self):
        return Artiste.objects.filter(
            Q(musiques__musiqueplaylist__playlist=self)
            | Q(remixes__musiqueplaylist__playlist=self)
            | Q(musiques_featuring__musiqueplaylist__playlist=self)
        ).distinct()


class Artiste(models.Model):
    nom_artiste = models.CharField("nom d'artiste", max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    prenom = models.CharField('prénom', max_length=100, blank=True)
    nom = models.CharField(max_length=100, blank=True)
    styles = models.ManyToManyField(Style, related_name='artistes', blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.ForeignKey(Pays, on_delete=models.SET_NULL, null=True, blank=True)
    site_web = models.URLField(blank=True)
    mail_contact = models.EmailField('adresse mail de contact', blank=True)
    telephone_contact = models.CharField('téléphone de contact', max_length=15, blank=True)
    cachet = models.DecimalField(
        help_text="Il s'agit du prix moyen pour booker l'artiste.",
        validators=[MinValueValidator(0)],
        max_digits=7, decimal_places=2,
        null=True, blank=True)
    facebook_id = models.BigIntegerField(null=True, blank=True)
    soundcloud_id = models.BigIntegerField(null=True, blank=True)
    spotify_id = models.BigIntegerField(null=True, blank=True)
    createur = models.ForeignKey(
        Profil, related_name='artistes_crees', on_delete=models.SET_NULL, null=True, blank=True
    )
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    date_modification = models.DateTimeField('dernière modification', auto_now=True)

    class Meta:
        ordering = ('nom_artiste',)

    def __str__(self):
        return self.nom_artiste

    def get_absolute_url(self):
        return reverse('music:detail-artiste', kwargs={'slug': self.slug})

    def full_name(self):
        if self.nom and self.prenom:
            return self.prenom + ' ' + self.nom
        return None

    def all_musics(self):
        return Musique.objects.filter(Q(artiste=self) | Q(remixed_by=self) | Q(featuring=self))

    def playlists(self):
        return Playlist.objects.filter(
            Q(musiqueplaylist__musique__artiste=self)
            | Q(musiqueplaylist__musique__remixed_by=self)
            | Q(musiqueplaylist__musique__featuring=self)
        ).distinct()

    @property
    def soundcloud_followers(self):
        # client = soundcloud.Client(client_id=YOUR_CLIENT_ID)
        # L'API de Soundcloud ne propose plus de Client ID :
        # https://docs.google.com/forms/d/e/1FAIpQLSfNxc82RJuzC0DnISat7n4H-G7IsPQIdaMpe202iiHZEoso9w/closedform
        return random.randint(1, 10000)


class Musique(models.Model):
    titre = models.CharField(max_length=50)
    slug = models.SlugField()
    artiste = models.ForeignKey(
        Artiste,
        on_delete=models.PROTECT,
        related_name='musiques',
        help_text='Artiste principal de la musique.'
    )
    featuring = models.ManyToManyField(
        Artiste,
        help_text='Les artistes qui ont participé à la musique.',
        related_name='musiques_featuring',
        blank=True
    )
    remixed_by = models.ForeignKey(
        Artiste,
        verbose_name='remixé par',
        on_delete=models.PROTECT,
        related_name='remixes',
        null=True, blank=True
    )
    album = models.CharField(max_length=200, blank=True)
    styles = models.ManyToManyField(Style, related_name='musiques', blank=True)
    playlists = models.ManyToManyField(Playlist, related_name='musiques', blank=True, through='MusiquePlaylist')
    createur = models.ForeignKey(
        Profil, related_name='musiques_crees', on_delete=models.SET_NULL, null=True, blank=True
    )
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    date_modification = models.DateTimeField('dernière modification', auto_now=True)

    class Meta:
        ordering = ('artiste__nom_artiste', 'titre')
        unique_together = ('artiste', 'titre')

    def __str__(self):
        return '%s - %s' % (self.artiste_display(), self.titre_display())

    def artiste_display(self):
        if self.featuring.exists():
            return '%s & %s' % (self.artiste, ' & '.join(self.featuring.values_list('nom_artiste', flat=True)))
        return self.artiste.nom_artiste
    artiste_display.short_description = 'Artistes'
    artiste_display.admin_order_field = 'artiste'

    def titre_display(self):
        if self.remixed_by:
            return '%s (%s Remix)' % (self.titre, self.remixed_by.nom_artiste)
        return self.titre
    titre_display.short_description = 'Titre'
    titre_display.admin_order_field = 'titre'

    def get_absolute_url(self):
        return reverse('music:detail-musique',
                       kwargs={'slug_artist': self.artiste.slug, 'slug': self.slug, 'pk': self.pk})

    def nb_vue(self):
        # TODO Essayer d'utiliser une aggrégation
        return sum((lien.click_count for lien in self.liens.all()))

    nb_vue.short_description = 'Nombre de vue'


class MusiquePlaylist(SortableMixin):
    playlist = SortableForeignKey(Playlist, on_delete=models.CASCADE)
    musique = models.ForeignKey(Musique, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    date_ajout = models.DateTimeField("date d'ajout de la musique dans la playlist", auto_now_add=True)

    class Meta:
        verbose_name = 'Musique de la playlist'
        verbose_name_plural = 'Musiques de la playlist'
        unique_together = (('playlist', 'musique'),)
        ordering = ('position',)


class Lien(models.Model):
    musique = models.ForeignKey(Musique, on_delete=models.CASCADE, related_name='liens')
    url = models.URLField('lien vers la musique')
    createur = models.ForeignKey(Profil, related_name='liens_crees', on_delete=models.SET_NULL, null=True, blank=True)
    SOUNDCLOUD = 'SC'
    YOUTUBE = 'YT'
    SPOTIFY = 'SP'
    PLATEFORMES_MUSIQUE = [
        (SOUNDCLOUD, 'Soundcloud'),
        (YOUTUBE, 'YouTube'),
        (SPOTIFY, 'Spotify')
    ]
    plateforme = models.CharField(max_length=2, choices=PLATEFORMES_MUSIQUE, blank=True)
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    click_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '(%s) %s' % (self.get_plateforme_display(), self.url)


class Label(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    styles = models.ManyToManyField(Style, related_name='labels', blank=True)
    artistes = models.ManyToManyField(Artiste, related_name='labels', blank=True)

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return self.nom
