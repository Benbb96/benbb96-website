from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from avis.models import Profil


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)
