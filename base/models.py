from django.db import models


class Projet(models.Model):
    nom = models.CharField(max_length=100)
    lien = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="media/projet/")
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom