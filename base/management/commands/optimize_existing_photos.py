"""
Optimise les photos existantes stockées dans GCS (ou un répertoire local de backup).

Pour chaque entrée en base dont la photo n'est pas déjà en WebP :
  1. Ouvre le fichier depuis --source-dir (backup) ou le storage Django (GCS en prod).
  2. Applique la rotation EXIF, redimensionne à 1280 px max, réencode en WebP q80.
  3. Écrit le fichier optimisé dans le storage Django (GCS ou local).
  4. Met à jour le champ photo en base (nouveau nom .webp).

Usage typique :
  # Prévisualisation depuis le backup local
  python manage.py optimize_existing_photos --source-dir ~/backups/bucket-refonte-2026-05-29 --dry-run

  # Exécution réelle depuis le backup (nécessite GCS configuré en prod)
  python manage.py optimize_existing_photos --source-dir ~/backups/bucket-refonte-2026-05-29

  # Exécution directement depuis GCS (si configuré)
  python manage.py optimize_existing_photos
"""

import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from avis.models import Avis
from kendama.models import Kendama
from my_spot.models import SpotPhoto
from super_moite_moite.models import Tache

MODELS = [
    ('Avis', Avis),
    ('Kendama', Kendama),
    ('SpotPhoto', SpotPhoto),
    ('Tache', Tache),
]

MAX_WIDTH = 1280
WEBP_QUALITY = 80


def optimize_image(file_obj):
    """Ouvre, corrige la rotation EXIF, redimensionne et réencode en WebP. Retourne BytesIO."""
    from PIL import Image, ImageOps

    img = Image.open(file_obj)
    img.load()
    img = ImageOps.exif_transpose(img)

    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode in ('RGBA', 'LA'):
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img.convert('RGBA'), mask=img.convert('RGBA').split()[-1])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    if img.width > MAX_WIDTH:
        new_height = int(img.height * MAX_WIDTH / img.width)
        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

    output = BytesIO()
    img.save(output, format='WEBP', quality=WEBP_QUALITY)
    output.seek(0)
    return output, img.size


class Command(BaseCommand):
    help = 'Optimise (resize + WebP) les photos existantes des modèles PhotoAbstract'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            help=(
                'Répertoire racine contenant le backup du bucket '
                '(ex. ~/backups/bucket-refonte-2026-05-29). '
                'Sans cette option, les fichiers sont lus depuis le storage Django.'
            )
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Affiche ce qui serait fait sans modifier le storage ni la base."
        )
        parser.add_argument(
            '--limit', type=int, default=0,
            help="Traite au plus N images au total (utile pour tester)."
        )
        parser.add_argument(
            '--model', choices=[m for m, _ in MODELS],
            help="Restreint le traitement à un seul modèle."
        )

    def handle(self, *args, **options):
        from PIL import Image  # noqa: F401 — vérifie que Pillow est dispo

        dry_run = options['dry_run']
        source_dir = options.get('source_dir')
        limit = options['limit']
        model_filter = options.get('model')

        if source_dir:
            source_dir = os.path.expanduser(source_dir)
            if not os.path.isdir(source_dir):
                raise CommandError(f"--source-dir {source_dir!r} n'existe pas.")

        if dry_run:
            self.stdout.write(self.style.WARNING('Mode dry-run — aucune modification.'))

        total_done = total_skip = total_error = 0

        models_to_process = [
            (label, Model) for label, Model in MODELS
            if not model_filter or label == model_filter
        ]

        for label, Model in models_to_process:
            self.stdout.write(f'\n── {label} ──')
            qs = Model.objects.exclude(photo='').exclude(photo__isnull=True)
            done = skip = error = 0

            for obj in qs.iterator():
                if limit and (total_done + done) >= limit:
                    break

                raw = obj.photo.name or ''
                if not raw or raw == 'placeholder.jpg' or raw.startswith('http'):
                    skip += 1
                    continue

                if raw.lower().endswith('.webp'):
                    self.stdout.write(f'  SKIP {raw} (déjà WebP)')
                    skip += 1
                    continue

                # Chemin de lecture depuis le backup (peut contenir 'media/' — structure Firebase)
                read_path = raw
                # Chemin de stockage : sans préfixe 'media/' car GS_LOCATION/MEDIA_URL l'ajoute
                storage_path = raw[len('media/'):] if raw.startswith('media/') else raw
                new_storage_name = os.path.splitext(storage_path)[0] + '.webp'

                try:
                    orig_size = self._get_file_size(read_path, source_dir)
                    file_obj = self._open_file(read_path, source_dir)
                    if file_obj is None:
                        self.stdout.write(self.style.WARNING(f'  MANQUANT {read_path}'))
                        error += 1
                        continue

                    output, (w, h) = optimize_image(file_obj)
                    new_size = output.getbuffer().nbytes

                    ratio = (1 - new_size / orig_size) * 100 if orig_size else 0
                    self.stdout.write(
                        f'  {"[DRY] " if dry_run else ""}'
                        f'{raw} → {new_storage_name}  '
                        f'{orig_size // 1024} Ko → {new_size // 1024} Ko  '
                        f'({ratio:.0f}% de réduction)  {w}×{h}'
                    )

                    if not dry_run:
                        if default_storage.exists(new_storage_name):
                            default_storage.delete(new_storage_name)
                        default_storage.save(new_storage_name, ContentFile(output.read()))
                        obj.photo = new_storage_name
                        obj.save(update_fields=['photo'])

                    done += 1

                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f'  ERREUR {raw}: {exc}'))
                    error += 1

            self.stdout.write(
                f'  → {done} optimisée(s), {skip} ignorée(s), {error} erreur(s)'
            )
            total_done += done
            total_skip += skip
            total_error += error

        self.stdout.write(self.style.SUCCESS(
            f'\nTotal : {total_done} optimisée(s), {total_skip} ignorée(s), {total_error} erreur(s).'
        ))

    def _storage_name(self, path):
        """Retire le préfixe 'media/' hérité de Firebase — GS_LOCATION le rajoute côté GCS."""
        return path[len('media/'):] if path.startswith('media/') else path

    def _open_file(self, path, source_dir=None):
        """Ouvre le fichier depuis source_dir ou depuis le storage Django."""
        if source_dir:
            full = os.path.join(source_dir, path)
            if not os.path.isfile(full):
                return None
            return open(full, 'rb')
        try:
            return default_storage.open(self._storage_name(path))
        except Exception:
            return None

    def _get_file_size(self, path, source_dir=None):
        """Retourne la taille du fichier source en octets."""
        if source_dir:
            full = os.path.join(source_dir, path)
            return os.path.getsize(full) if os.path.isfile(full) else 0
        try:
            return default_storage.size(self._storage_name(path))
        except Exception:
            return 0
