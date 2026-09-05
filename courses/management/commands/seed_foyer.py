"""
Charge des rayons et des articles dans un foyer existant, depuis un fichier JSON.

Le fichier par défaut (docs/courses/seed-poc.json) est un **échantillon générique** versionné
dans le dépôt, qui sert d'exemple de format et de jeu de départ neutre. L'inventaire réel d'un
foyer n'a rien à faire dans un dépôt public : on le dépose sur le serveur et on le passe à
`--fichier`.

Le foyer n'est pas créé par cette commande : Rayon et Article portent une FK vers Foyer, donc
il doit déjà exister (créé via l'admin). Idempotent — rejouable sans dupliquer
(get_or_create sur (foyer, nom)) : `db.sqlite3` est gitignoré, dev et prod ont des bases
indépendantes, donc le seed doit être rejoué à la main sur chacune.

Format attendu :
    {
      "rayons":   [{"nom": …, "ordre": …}],
      "articles": [{"nom": …, "rayon": …, "unite": …, "conditionnement": …,
                    "stock_cible": …, "stock_reference": …}]
    }

Usage :
    python manage.py seed_foyer <slug-foyer>
    python manage.py seed_foyer <slug-foyer> --fichier ~/inventaire-maison.json
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from courses.models import Article, Foyer, Rayon

SEED_PATH = Path(__file__).resolve().parents[3] / "docs" / "courses" / "seed-poc.json"


class Command(BaseCommand):
    help = "Charge les rayons et articles d'un fichier JSON dans un foyer existant."

    def add_arguments(self, parser):
        parser.add_argument("foyer_slug", help="Slug du foyer à peupler.")
        parser.add_argument(
            "--fichier",
            default=str(SEED_PATH),
            help=(
                "Chemin du JSON à charger. Par défaut l'échantillon générique versionné "
                "(docs/courses/seed-poc.json) ; passer ici l'inventaire réel du foyer, "
                "qui lui reste hors du dépôt."
            ),
        )

    def handle(self, *args, **options):
        slug = options["foyer_slug"]
        try:
            foyer = Foyer.objects.get(slug=slug)
        except Foyer.DoesNotExist as err:
            raise CommandError(
                f"Aucun foyer avec le slug {slug!r} — créez-le d'abord depuis l'admin."
            ) from err

        chemin = Path(options["fichier"]).expanduser()
        try:
            data = json.loads(chemin.read_text(encoding="utf-8"))
        except FileNotFoundError as err:
            raise CommandError(f"Fichier introuvable : {chemin}") from err
        except json.JSONDecodeError as err:
            raise CommandError(f"JSON invalide dans {chemin} : {err}") from err

        self._valide(data, chemin)

        rayons_par_nom = {}
        rayons_crees = 0
        for rayon_data in data["rayons"]:
            rayon, created = Rayon.objects.get_or_create(
                foyer=foyer,
                nom=rayon_data["nom"],
                defaults={"ordre": rayon_data["ordre"]},
            )
            rayons_par_nom[rayon_data["nom"]] = rayon
            rayons_crees += int(created)

        articles_crees = 0
        for article_data in data["articles"]:
            _, created = Article.objects.get_or_create(
                foyer=foyer,
                nom=article_data["nom"],
                defaults={
                    "rayon": rayons_par_nom[article_data["rayon"]],
                    # `unite` est l'unité de CONSOMMATION, pas d'achat (conception.md §10.3) :
                    # une recette dose en grammes ou en millilitres, jamais en paquets.
                    # Vide = pas encore confirmée, comme pour un article importé (§9 étape 3).
                    "unite": article_data.get("unite", ""),
                    "conditionnement": article_data.get("conditionnement", 1),
                    # Le « want » et le « have » du POC. Sans `stock_cible`, le besoin
                    # calculé reste nul et « À acheter » s'affiche vide après le seed.
                    "stock_cible": article_data.get("stock_cible", 0),
                    "stock_reference": article_data.get("stock_reference", 0),
                },
            )
            articles_crees += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"{rayons_crees} rayon(s) et {articles_crees} article(s) créé(s) "
                f"pour {foyer} depuis {chemin.name}."
            )
        )

    def _valide(self, data, chemin):
        """
        Échoue tôt et clairement plutôt que de laisser un KeyError remonter au milieu de
        l'insertion : le fichier vient de l'extérieur du dépôt, il peut être n'importe quoi.
        """
        for cle in ("rayons", "articles"):
            if not isinstance(data.get(cle), list):
                raise CommandError(f"{chemin} : clé {cle!r} absente ou pas une liste.")

        rayons = {r["nom"] for r in data["rayons"]}

        noms = [a["nom"] for a in data["articles"]]
        doublons = sorted({n for n in noms if noms.count(n) > 1})
        if doublons:
            # get_or_create porte sur (foyer, nom) : un homonyme serait avalé en silence.
            raise CommandError(
                f"{chemin} : articles en double, ils seraient fusionnés — {doublons}"
            )

        inconnus = sorted({a["rayon"] for a in data["articles"]} - rayons)
        if inconnus:
            raise CommandError(
                f"{chemin} : rayons référencés mais non déclarés — {inconnus}"
            )
