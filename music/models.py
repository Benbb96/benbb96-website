import soundcloud
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Pays(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Pays'

    def __str__(self):
        return self.nom


class Style(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom


class Artiste(models.Model):
    nom_artiste = models.CharField("nom d'artiste", max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    nom = models.CharField(max_length=100, blank=True)
    prenom = models.CharField('prénom', max_length=100, blank=True)
    styles = models.ManyToManyField(Style, related_name='artistes', blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.ForeignKey(Pays, on_delete=models.PROTECT, blank=True)
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
    createur = models.ForeignKey(User, related_name='artistes_crees', on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date de création", auto_now_add=True)
    date_modification = models.DateTimeField(verbose_name="dernière modification", auto_now=True)

    def __str__(self):
        return self.nom_artiste

    @property
    def soundcloud_followers(self):
        # client = soundcloud.Client(client_id=YOUR_CLIENT_ID)
        return 4


class Label(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    styles = models.ManyToManyField(Style, related_name='labels', blank=True)
    artistes = models.ManyToManyField(Artiste, related_name='labels', blank=True)

    def __str__(self):
        return self.nom
