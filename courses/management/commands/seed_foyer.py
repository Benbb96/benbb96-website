"""
Charge les rayons et articles du POC (docs/courses/seed-poc.json) dans un foyer existant.

Le foyer n'est pas créé par cette commande : Rayon et Article portent une FK vers Foyer, donc
il doit déjà exister (créé via l'admin). Idempotent — rejouable sans dupliquer
(get_or_create sur (foyer, nom)) : `db.sqlite3` est gitignoré, dev et prod ont des bases
indépendantes, donc le seed doit être rejoué à la main sur chacune.

Usage :
    python manage.py seed_foyer <slug-foyer>
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from courses.models import Article, Foyer, Rayon

SEED_PATH = Path(__file__).resolve().parents[3] / "docs" / "courses" / "seed-poc.json"


class Command(BaseCommand):
    help = "Charge les rayons et articles de seed-poc.json dans un foyer existant."

    def add_arguments(self, parser):
        parser.add_argument("foyer_slug", help="Slug du foyer à peupler.")

    def handle(self, *args, **options):
        slug = options["foyer_slug"]
        try:
            foyer = Foyer.objects.get(slug=slug)
        except Foyer.DoesNotExist as err:
            raise CommandError(
                f"Aucun foyer avec le slug {slug!r} — créez-le d'abord depuis l'admin."
            ) from err

        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))

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
                    "unite": article_data["unite"],
                    "conditionnement": article_data["conditionnement"],
                },
            )
            articles_crees += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"{rayons_crees} rayon(s) et {articles_crees} article(s) créé(s) pour {foyer}."
            )
        )
