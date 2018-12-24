from django.core.validators import MinValueValidator
from django.db import models


class Pays(models.Model):
    nom = models.CharField(max_length=50, unique=True)

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


class Label(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    styles = models.ManyToManyField(Style, related_name='labels', blank=True)
    artistes = models.ManyToManyField(Artiste, related_name='labels', blank=True)

    def __str__(self):
        return self.nom
