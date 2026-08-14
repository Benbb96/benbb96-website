"""
Supprime du storage les fichiers media orphelins (plus référencés par aucun objet en base).

Sert à récupérer de l'espace après des suppressions/remplacements/optimisations : les
originaux non-WebP déréférencés, les images d'objets supprimés, etc.

Sécurités :
  - **dry-run par défaut** : il faut `--apply` pour supprimer réellement ;
  - ne balaie que le préfixe du storage media (location). Le préfixe `backups/` du bucket,
    situé HORS de `media/`, n'est jamais listé donc jamais touché ;
  - ignore les valeurs http (URLs externes) et `placeholder.jpg` côté références.

Usage :
    python manage.py clean_orphan_media           # aperçu (rien n'est supprimé)
    python manage.py clean_orphan_media --apply    # suppression réelle
"""

import os

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from base.image_utils import get_photo_models


class Command(BaseCommand):
    help = "Supprime les fichiers media du storage qui ne sont plus référencés en base."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Supprime réellement les orphelins. Par défaut : dry-run (affichage seul).",
        )

    def handle(self, *args, **options):
        apply = options["apply"]

        referenced = self._referenced_names()
        self.stdout.write(f"{len(referenced)} fichier(s) référencé(s) en base.")

        stored = self._stored_names()
        self.stdout.write(f"{len(stored)} fichier(s) présent(s) dans le storage media.")

        orphans = sorted(stored - referenced)
        if not orphans:
            self.stdout.write(self.style.SUCCESS("Aucun orphelin — rien à supprimer."))
            return

        if not apply:
            self.stdout.write(
                self.style.WARNING(
                    f"\nMode dry-run : {len(orphans)} orphelin(s) seraient supprimé(s). "
                    "Relance avec --apply pour supprimer réellement.\n"
                )
            )

        freed = 0
        deleted = 0
        for name in orphans:
            try:
                size = default_storage.size(name)
            except Exception:
                size = 0
            self.stdout.write(
                f"  {'[DRY] ' if not apply else ''}{name}  ({size // 1024} Ko)"
            )
            if apply:
                try:
                    default_storage.delete(name)
                    deleted += 1
                    freed += size
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR(f"  ERREUR suppression {name}: {exc}")
                    )

        if apply:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{deleted} orphelin(s) supprimé(s), ~{freed // (1024 * 1024)} Mo libéré(s)."
                )
            )
        else:
            total = sum(self._safe_size(n) for n in orphans)
            self.stdout.write(
                self.style.WARNING(f"~{total // (1024 * 1024)} Mo récupérables.")
            )

    def _safe_size(self, name):
        try:
            return default_storage.size(name)
        except Exception:
            return 0

    def _referenced_names(self):
        """
        Ensemble des noms (relatifs au storage, ex. 'avis/2024/1/5/x.webp') référencés en base.
        On retire un éventuel préfixe 'media/' hérité, et on ignore http/placeholder/vide.
        """
        names = set()
        for _label, Model, field in get_photo_models():
            qs = Model.objects.exclude(**{field: ""}).exclude(
                **{f"{field}__isnull": True}
            )
            for obj in qs.iterator():
                fieldfile = getattr(obj, field)
                raw = (fieldfile.name if fieldfile else "") or ""
                if not raw or raw == "placeholder.jpg" or raw.startswith("http"):
                    continue
                if raw.startswith("media/"):
                    raw = raw[len("media/") :]
                names.add(raw)
        return names

    def _stored_names(self):
        """
        Ensemble des noms présents dans le storage media (relatifs à la location), aussi bien
        pour le backend GCS (prod) que pour le FileSystemStorage local (dev).
        """
        # Backend GCS (django-storages) : on liste les blobs sous le préfixe `location`.
        client = getattr(default_storage, "client", None)
        bucket = getattr(default_storage, "bucket", None)
        location = (getattr(default_storage, "location", "") or "").strip("/")
        if client is not None and bucket is not None:
            prefix = f"{location}/" if location else ""
            names = set()
            for blob in client.list_blobs(bucket, prefix=prefix):
                if blob.name.endswith("/"):
                    continue
                rel = (
                    blob.name[len(prefix) :]
                    if prefix and blob.name.startswith(prefix)
                    else blob.name
                )
                if rel:
                    names.add(rel)
            return names

        # Backend local : parcours de MEDIA_ROOT.
        base = getattr(default_storage, "location", "")
        names = set()
        if base and os.path.isdir(base):
            for root, _dirs, files in os.walk(base):
                for fname in files:
                    rel = os.path.relpath(os.path.join(root, fname), base)
                    names.add(rel.replace(os.sep, "/"))
        return names
