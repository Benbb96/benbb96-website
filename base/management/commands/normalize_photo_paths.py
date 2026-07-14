"""
Normalise les chemins de photos hérités de Firebase dans la DB.

Les anciennes entrées stockent le chemin complet tel que produit par firebase-upload.js :
  media/avis/2024/1/5/fichier.jpg

ImageField s'attend au même chemin relatif à la racine du bucket GCS (ou MEDIA_ROOT).
Ce chemin est déjà le bon — la normalisation porte essentiellement sur :
  - Supprimer les valeurs "placeholder.jpg" (remplacées par NULL).
  - Logger les URL http complètes (rétrocompat gérée par photo_url, rien à changer).
  - Signaler les chemins qui ne pointent pas vers media/ pour investigation manuelle.

Idempotente : peut être rejouée sans risque.

Usage :
    python manage.py normalize_photo_paths [--dry-run]
"""

from django.core.management.base import BaseCommand

from avis.models import Avis
from kendama.models import Kendama
from my_spot.models import SpotPhoto
from super_moite_moite.models import Tache

MODELS = [
    ("Avis", Avis),
    ("Kendama", Kendama),
    ("SpotPhoto", SpotPhoto),
    ("Tache", Tache),
]


class Command(BaseCommand):
    help = "Normalise les chemins de photos Firebase vers ImageField GCS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les modifications sans les appliquer.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(
                self.style.WARNING("Mode dry-run — aucune modification en base.")
            )

        total_fixed = 0
        total_http = 0
        total_unknown = 0

        for label, Model in MODELS:
            fixed = http = unknown = 0
            qs = Model.objects.exclude(photo="").exclude(photo__isnull=True)
            for obj in qs.iterator():
                raw = obj.photo.name if obj.photo else ""
                if not raw:
                    continue

                if raw == "placeholder.jpg":
                    self.stdout.write(f"  {label} #{obj.pk}: placeholder → NULL")
                    if not dry_run:
                        obj.photo = None
                        obj.save(update_fields=["photo"])
                    fixed += 1

                elif raw.startswith("http"):
                    # URL complète : rétrocompat assurée par photo_url, rien à faire
                    http += 1

                elif raw.startswith("media/"):
                    # Ancien chemin Firebase avec préfixe 'media/' — on le retire car
                    # le storage (MEDIA_URL/GS_LOCATION) gère désormais ce préfixe.
                    new_path = raw[len("media/") :]
                    self.stdout.write(f"  {label} #{obj.pk}: {raw!r} → {new_path!r}")
                    if not dry_run:
                        obj.photo = new_path
                        obj.save(update_fields=["photo"])
                    fixed += 1

                elif "/" in raw:
                    # Chemin déjà normalisé (sans préfixe media/) — rien à faire
                    pass

                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  {label} #{obj.pk}: chemin inattendu {raw!r}"
                        )
                    )
                    unknown += 1

            self.stdout.write(
                f"{label}: {fixed} placeholder(s) nettoyé(s), "
                f"{http} URL http (rétrocompat), {unknown} chemin(s) inconnu(s)"
            )
            total_fixed += fixed
            total_http += http
            total_unknown += unknown

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal : {total_fixed} nettoyé(s), {total_http} URL http, {total_unknown} inconnu(s)."
            )
        )
