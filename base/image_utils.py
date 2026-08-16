"""
Optimisation d'images partagée : redimensionnement + conversion WebP.

Utilisé par PhotoAbstract.save() et PhotoOptimizationMixin.save() (base/models.py) pour optimiser
les nouveaux uploads à la volée.
"""

import os
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

MAX_WIDTH = 1280
WEBP_QUALITY = 80


def optimize_image_to_webp(file_obj, max_width=MAX_WIDTH, quality=WEBP_QUALITY):
    """
    Ouvre une image, applique la rotation EXIF, l'aplatit sur fond blanc en cas de
    transparence, la redimensionne à `max_width` px de large max et la réencode en WebP.

    Retourne un BytesIO positionné au début. Lève en cas d'image illisible.
    """
    from PIL import Image, ImageOps

    img = Image.open(file_obj)
    img.load()
    img = ImageOps.exif_transpose(img)

    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode in ("RGBA", "LA"):
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    if img.width > max_width:
        new_height = int(img.height * max_width / img.width)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    output = BytesIO()
    img.save(output, format="WEBP", quality=quality)
    output.seek(0)
    return output


def get_photo_models():
    """
    Liste des modèles porteurs d'une image, sous forme de tuples (label, Model, champ).

    Imports paresseux (dans la fonction) pour éviter tout import circulaire : ce module
    est importé par base.models, donc il ne doit pas importer les modèles au chargement.
    Source unique utilisée par la commande clean_orphan_media.
    """
    from avis.models import Avis
    from base.models import Profil, Projet
    from kendama.models import Kendama
    from my_spot.models import SpotPhoto
    from super_moite_moite.models import Tache
    from versus.models import Jeu

    return [
        ("Avis", Avis, "photo"),
        ("Kendama", Kendama, "photo"),
        ("SpotPhoto", SpotPhoto, "photo"),
        ("Tache", Tache, "photo"),
        ("Projet", Projet, "image"),
        ("Jeu", Jeu, "image"),
        ("Profil", Profil, "avatar"),
    ]


def optimize_uncommitted_fieldfile(fieldfile, field_name="photo"):
    """
    Si `fieldfile` est un nouvel upload non encore committé, retourne un InMemoryUploadedFile
    WebP optimisé à réassigner au champ. Sinon (champ vide, déjà en storage, ou image
    illisible) retourne None — l'appelant ne touche alors pas au champ.
    """
    if not fieldfile or getattr(fieldfile, "_committed", True):
        return None
    try:
        output = optimize_image_to_webp(fieldfile.file)
    except Exception:
        return None
    base_name = os.path.splitext(os.path.basename(fieldfile.name))[0]
    new_name = base_name + ".webp"
    return InMemoryUploadedFile(
        output, field_name, new_name, "image/webp", output.getbuffer().nbytes, None
    )
