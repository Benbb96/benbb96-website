from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from fontawesome.fields import IconField


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')  # La liaison OneToOne vers le modèle User
    avatar = models.ImageField(null=True, blank=True, upload_to="media/avatars/")
    date_creation = models.DateTimeField(verbose_name="date de création", auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profil', kwargs={'slug': self.user.username})

    @property
    def note_moyenne(self):
        return self.avis_set.all().aggregate(Avg('note'))['note__avg']


class Projet(models.Model):
    """
    Gestion des projets à afficher sur la page d'accueil
    """
    nom = models.CharField(max_length=100)
    lien = models.CharField(max_length=100, null=True, blank=True, help_text="Nom de la vue Django vers la page d'accueil du projet")
    image = models.ImageField(null=True, blank=True, upload_to="media/projet/")
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


class LienReseauSocial(models.Model):
    """
    Getsion des liens vers mes réseaux sociaux
    """
    reseau_social = IconField('réseau social')
    lien=models.URLField()
    ouvrir_nouvel_onglet = models.BooleanField(
        help_text="Indique s'il faut ouvrir le lien dans un nouvel onglet",
        default=False
    )
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'lien réseau social'
        verbose_name_plural = 'liens réseaux sociaux'

    def __str__(self):
        return str(self.reseau_social)