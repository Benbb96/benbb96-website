from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html
from taggit.managers import TaggableManager


class Profil(models.Model):
    class Meta:
        verbose_name = 'Profil'

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # La liaison OneToOne vers le modèle User
    avatar = models.ImageField(null=True, blank=True, upload_to="media/avatars/")
    date = models.DateTimeField(verbose_name="date de création", auto_now_add=True)

    def __str__(self):
        return self.user.username


class Restaurant(models.Model):
    class Meta:
        verbose_name = 'Restaurant'

    nom = models.CharField(max_length=100)
    informations = models.TextField(blank=True, help_text='Informations utiles et relatives au restaurant')
    adresse = models.CharField(max_length=200, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    date = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    def __str__(self):
        return self.nom


class Plat(models.Model):
    class Meta:
        verbose_name = 'Plat'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text='Une description du plat')
    tags = TaggableManager()
    prix = models.DecimalField(max_digits=4, decimal_places=2)
    photo = models.ImageField(null=True, blank=True, upload_to="media/plats/")
    date = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    def __str__(self):
        return self.nom


class Avis(models.Model):
    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'avis'

    plat = models.ForeignKey(Plat, on_delete=models.PROTECT)
    auteur = models.ForeignKey(Profil, on_delete=models.PROTECT)
    avis = models.TextField(blank=True, help_text='Ton avis en quelques mots sur le plat')
    note = models.PositiveIntegerField(default=5, help_text='Une note entre 0 et 10',
                                       validators=[MinValueValidator(0), MaxValueValidator(10)])
    photo = models.ImageField(null=True, blank=True, upload_to="avis/")
    date = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    def __str__(self):
        return str(self.auteur) + ' : ' + self.plat.nom + ' (' + str(self.note) + '/10)'