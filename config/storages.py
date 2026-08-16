"""Backends de stockage — voir STORAGES dans config/settings/prod.py."""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class NonStrictCompressedManifestStaticFilesStorage(
    CompressedManifestStaticFilesStorage
):
    """Manifest WhiteNoise tolérant aux entrées manquantes.

    django-fontawesome-6 appelle `static()` au moment de l'import du module
    (fontawesome_6/widgets.py : `css_admin = get_css_admin()`), donc dès que
    base.models importe IconField. Avec un manifest strict, toute commande qui
    charge les modèles — `migrate` en tête — explose sur
    `ValueError: Missing staticfiles manifest entry` tant que collectstatic
    n'a pas tourné. Or le déploiement lance migrate AVANT collectstatic : au
    premier déploiement, le manifest n'existe pas encore et le déploiement
    casse.

    manifest_strict = False fait retomber ces appels sur l'URL non hashée au
    lieu de lever. Les fichiers absents du manifest perdent juste le
    `immutable` (WhiteNoise leur applique max-age=60) ; tous les autres, servis
    via {% static %} après collectstatic, gardent le cache d'un an.
    """

    manifest_strict = False
