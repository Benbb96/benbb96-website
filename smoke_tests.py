"""
Tests de smoke
==============
Filet de sécurité de non-régression. Couvre :
  1. Status 200 des vues publiques clés
  2. Redirect (302) des vues login_required sans auth
  3. Non-régression de l'API tracker
  4. Non-régression de l'API super_moite_moite
  5. Obtention/rafraîchissement de token JWT
  6. Validité des `profil_lookup` des admins scopés (base.admin.ProfilScopedAdmin)
  7. Squelette de l'app courses (phase 0) : modèles, calculs et seed_foyer
  8. Vues de l'app courses (phase 1) : annotation de besoin, À acheter / Inventaire / Historique

Lancer : python manage.py test smoke_tests
"""

import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone, translation
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import (
    Article,
    DemandePonctuelle,
    Etiquette,
    Foyer,
    Ligne,
    MouvementStock,
    Rayon,
    Sortie,
)


def url(name, *args, lang="fr", **kwargs):
    """Reverse une URL dans la locale française (valeur par défaut du projet)."""
    from django.urls import reverse

    with translation.override(lang):
        return reverse(name, args=args, kwargs=kwargs)


# ---------------------------------------------------------------------------
# 1. Vues publiques
# ---------------------------------------------------------------------------


class PublicViewsSmokeTest(TestCase):
    """Les vues publiques doivent répondre HTTP 200."""

    def _get200(self, view_name, *args, **kwargs):
        r = self.client.get(url(view_name, *args, **kwargs))
        self.assertEqual(
            r.status_code,
            200,
            f"Vue {view_name!r} → attendu 200, obtenu {r.status_code}",
        )

    def test_home(self):
        self._get200("base:home")

    def test_about(self):
        self._get200("base:about")

    def test_signup(self):
        self._get200("base:signup")

    def test_login(self):
        self._get200("login")

    def test_gallery(self):
        self._get200("base:gallery")

    def test_robots_txt(self):
        r = self.client.get(url("robots_file"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "text/plain")

    def test_sitemap(self):
        self._get200("django.contrib.sitemaps.views.sitemap")

    def test_music_list(self):
        self._get200("music:liste-musiques")

    def test_versus_jeux(self):
        self._get200("versus:liste-jeux")

    def test_avis_list(self):
        self._get200("avis:liste-avis")

    def test_kendama_tricks(self):
        self._get200("kendama:tricks")


# ---------------------------------------------------------------------------
# 2. Vues login_required → redirect
# ---------------------------------------------------------------------------


class AuthRequiredViewsSmokeTest(TestCase):
    """Les vues protégées redirigent vers /login/ sans authentification."""

    def _expect_redirect(self, view_name):
        r = self.client.get(url(view_name))
        self.assertEqual(
            r.status_code,
            302,
            f"Vue {view_name!r} → attendu 302, obtenu {r.status_code}",
        )

    def test_tracker_list_requires_login(self):
        self._expect_redirect("tracker:liste-tracker")

    def test_smm_logements_requires_login(self):
        self._expect_redirect("super-moite-moite:liste-logements")

    def test_courses_mes_foyers_requires_login(self):
        self._expect_redirect("courses:mes-foyers")


# ---------------------------------------------------------------------------
# 3. API Tracker
# ---------------------------------------------------------------------------


class TrackerAPITest(TestCase):
    """Non-régression des endpoints API tracker (DRF + JWT)."""

    def setUp(self):
        self.user = User.objects.create_user("smoke_tracker", password="testpass123!")
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def _get200(self, view_name, query=""):
        r = self.api.get(url(view_name) + query)
        self.assertEqual(
            r.status_code,
            status.HTTP_200_OK,
            f"API {view_name!r}{query} → {r.status_code}",
        )
        return r

    def test_api_root(self):
        self._get200("tracker:api-root")

    def test_tracker_list(self):
        r = self._get200("tracker:tracker-list")
        self.assertIsInstance(r.data, list)

    def test_tracker_list_light_serializer(self):
        """tracks=0 → TrackerLightSerializer (endpoint montre connectée)."""
        self._get200("tracker:tracker-list", "?tracks=0")

    def test_track_list(self):
        r = self._get200("tracker:track-list")
        self.assertIsInstance(r.data, list)

    def test_unauthenticated_tracker_is_rejected(self):
        anon = APIClient()
        r = anon.get(url("tracker:tracker-list"))
        self.assertIn(
            r.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            "L'API tracker doit rejeter les requêtes non authentifiées",
        )


# ---------------------------------------------------------------------------
# 4. API Super Moite Moite
# ---------------------------------------------------------------------------


class SMMAPITest(TestCase):
    """Non-régression des endpoints API super_moite_moite."""

    def setUp(self):
        self.user = User.objects.create_user("smoke_smm", password="testpass123!")
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def _get200(self, view_name):
        r = self.api.get(url(view_name))
        self.assertEqual(
            r.status_code, status.HTTP_200_OK, f"API {view_name!r} → {r.status_code}"
        )
        return r

    def test_api_root(self):
        self._get200("super-moite-moite:api-root")

    def test_logements_list(self):
        self._get200("super-moite-moite:logement-list")

    def test_categories_list(self):
        self._get200("super-moite-moite:categorie-list")

    def test_taches_list(self):
        self._get200("super-moite-moite:tache-list")

    def test_point_taches_list(self):
        self._get200("super-moite-moite:point_tache-list")

    def test_track_taches_list(self):
        self._get200("super-moite-moite:track_tache-list")

    def test_unauthenticated_smm_is_rejected(self):
        anon = APIClient()
        r = anon.get(url("super-moite-moite:logement-list"))
        self.assertIn(
            r.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            "L'API SMM doit rejeter les requêtes non authentifiées",
        )


# ---------------------------------------------------------------------------
# 5. JWT — obtain & refresh
# ---------------------------------------------------------------------------


class JWTAuthSmokeTest(TestCase):
    """Les endpoints JWT fonctionnent et retournent les tokens attendus."""

    def setUp(self):
        User.objects.create_user("smoke_jwt", password="testpass123!")
        self.api = APIClient()

    def test_token_obtain(self):
        r = self.api.post(
            url("token_obtain_pair"),
            {"username": "smoke_jwt", "password": "testpass123!"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("access", r.data)
        self.assertIn("refresh", r.data)

    def test_token_refresh(self):
        obtain = self.api.post(
            url("token_obtain_pair"),
            {"username": "smoke_jwt", "password": "testpass123!"},
            format="json",
        )
        r = self.api.post(
            url("token_refresh"), {"refresh": obtain.data["refresh"]}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("access", r.data)


# ---------------------------------------------------------------------------
# 6. Admins scopés au profil
# ---------------------------------------------------------------------------


class AdminProfilScopeTest(TestCase):
    """
    Chaque `profil_lookup` déclaré doit être un chemin d'ORM valide.

    Un lookup erroné ne lève qu'à l'exécution, et uniquement pour un utilisateur
    non-superuser : c'est ainsi qu'un `…__habitants_` (underscore parasite) a survécu
    six ans dans super_moite_moite sans que personne ne passe par ce chemin.
    """

    def test_tous_les_profil_lookup_sont_valides(self):
        profil = User.objects.create_user("scope-test").profil

        scopes = [
            (model, model_admin)
            for model, model_admin in admin.site._registry.items()
            if getattr(model_admin, "profil_lookup", None)
        ]
        self.assertGreater(len(scopes), 0, "aucun admin scopé n'a été trouvé")

        for model, model_admin in scopes:
            with self.subTest(admin=type(model_admin).__name__):
                # Lève FieldError si le lookup ne correspond à aucun chemin réel.
                model.objects.filter(**{model_admin.profil_lookup: profil}).exists()


# ---------------------------------------------------------------------------
# 7. App courses (phase 0) — modèles, calculs et seed_foyer
# ---------------------------------------------------------------------------


class CoursesModelsSmokeTest(TestCase):
    """Contraintes de modèles posées en §5/§5.1/§7.1 de conception.md."""

    def setUp(self):
        user = User.objects.create_user("smoke_courses", password="testpass123!")
        self.profil = user.profil
        self.foyer = Foyer.objects.create(nom="Foyer smoke test")
        self.article = Article.objects.create(foyer=self.foyer, nom="Lait")

    def test_foyer_slug_auto_genere(self):
        self.assertEqual(self.foyer.slug, "foyer-smoke-test")

    def test_un_article_une_fois_par_sortie(self):
        """UniqueConstraint(fields=["sortie", "article"]) — doublon dans la même sortie rejeté."""
        sortie = Sortie.objects.create(foyer=self.foyer, cree_par=self.profil)
        Ligne.objects.create(sortie=sortie, article=self.article)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Ligne.objects.create(sortie=sortie, article=self.article)

    def test_meme_article_dans_deux_sorties_ouvertes_autorise(self):
        """§5.1 : la règle « une seule sortie ouverte » est applicative, pas une contrainte dure."""
        sortie_1 = Sortie.objects.create(
            foyer=self.foyer, cree_par=self.profil, nom="Semaine"
        )
        sortie_2 = Sortie.objects.create(
            foyer=self.foyer, cree_par=self.profil, nom="Apéro"
        )
        Ligne.objects.create(sortie=sortie_1, article=self.article)
        Ligne.objects.create(sortie=sortie_2, article=self.article)
        self.assertEqual(Ligne.objects.filter(article=self.article).count(), 2)

    def test_etiquette_meme_nom_dans_deux_foyers(self):
        """L'unicité porte sur (foyer, nom) : deux foyers peuvent avoir leur « Apéro »."""
        autre = Foyer.objects.create(nom="Chez les parents")
        Etiquette.objects.create(foyer=self.foyer, nom="Apéro")
        Etiquette.objects.create(foyer=autre, nom="Apéro")

    def test_etiquette_doublon_actif_rejete(self):
        Etiquette.objects.create(foyer=self.foyer, nom="Bio")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Etiquette.objects.create(foyer=self.foyer, nom="Bio")


class SeedFoyerCommandTest(TestCase):
    """La commande seed_foyer (management command, pas data migration — cf. conception.md §10)."""

    def setUp(self):
        self.foyer = Foyer.objects.create(nom="Foyer seed test")

    def test_seed_foyer_charge_le_poc(self):
        call_command("seed_foyer", self.foyer.slug)
        self.assertEqual(Rayon.objects.filter(foyer=self.foyer).count(), 10)
        self.assertEqual(Article.objects.filter(foyer=self.foyer).count(), 49)

    def test_seed_foyer_idempotent(self):
        call_command("seed_foyer", self.foyer.slug)
        call_command("seed_foyer", self.foyer.slug)
        self.assertEqual(Rayon.objects.filter(foyer=self.foyer).count(), 10)
        self.assertEqual(Article.objects.filter(foyer=self.foyer).count(), 49)

    def test_seed_foyer_charge_les_unites_de_consommation(self):
        """L'unité est celle dont une recette parle (§10.3), pas l'unité d'achat."""
        call_command("seed_foyer", self.foyer.slug)
        farine = Article.objects.get(foyer=self.foyer, nom="Farine")
        self.assertEqual(farine.unite, "g")
        self.assertEqual(farine.conditionnement, Decimal(1000))
        # Ce qu'une recette compte à l'unité le reste : « 3 œufs », pas « 150 g d'œufs ».
        oeufs = Article.objects.get(foyer=self.foyer, nom="Oeufs")
        self.assertEqual(oeufs.unite, "unite")

    def test_seed_foyer_slug_inconnu(self):
        with self.assertRaises(CommandError):
            call_command("seed_foyer", "slug-qui-nexiste-pas")


class ArticleStockEstimeTest(TestCase):
    """
    Le cœur de l'app (conception.md §4) : le stock n'est pas saisi, il fond tout seul.
    Une régression ici fausserait toutes les suggestions sans rien casser de visible.
    """

    def setUp(self):
        self.foyer = Foyer.objects.create(nom="Chez nous")

    def _article(self, **kwargs):
        defauts = {
            "foyer": self.foyer,
            "nom": "Couches taille 4",
            "stock_reference": Decimal(40),
            "stock_maj_le": timezone.now() - timedelta(days=10),
            "conso_amorce": Decimal(1),
        }
        return Article.objects.create(**{**defauts, **kwargs})

    def test_le_stock_decroit_avec_le_temps(self):
        # 40 achetées il y a 10 jours, 1 par jour → il doit en rester 30.
        self.assertAlmostEqual(float(self._article().stock_estime), 30.0, places=3)

    def test_le_stock_ne_descend_jamais_sous_zero(self):
        article = self._article(stock_maj_le=timezone.now() - timedelta(days=400))
        self.assertEqual(article.stock_estime, Decimal(0))

    def test_l_estimation_apprise_prime_sur_la_graine(self):
        # conso_amorce=1 mais estimation=2 → l'estimation gagne, la graine devient inerte.
        article = self._article(conso_par_jour_estimee=Decimal(2))
        self.assertAlmostEqual(float(article.stock_estime), 20.0, places=3)

    def test_sans_suivi_auto_le_stock_reste_fige(self):
        article = self._article(suivi_auto=False)
        self.assertEqual(article.stock_estime, Decimal(40))

    def test_sans_consommation_connue_le_stock_reste_fige(self):
        article = self._article(conso_amorce=None)
        self.assertEqual(article.stock_estime, Decimal(40))


# ---------------------------------------------------------------------------
# 8. App courses (phase 1) — annotation de besoin et vues
# ---------------------------------------------------------------------------


class ArticleAnnotationBesoinTest(TestCase):
    """
    `Article.stock_estime`/`conso_retenue` restent des property Python (§5) ; `avec_besoin()`
    doit produire le même nombre par annotation SQL (§10.4). Verrouille l'alignement des deux
    expressions — une régression ici fausserait « À acheter » sans rien casser de visible.
    """

    def setUp(self):
        self.foyer = Foyer.objects.create(nom="Foyer annotation")

    def _article(self, **kwargs):
        defauts = {
            "foyer": self.foyer,
            "nom": "Couches",
            "stock_cible": Decimal(40),
            "stock_reference": Decimal(40),
            "stock_maj_le": timezone.now() - timedelta(days=10),
            "conso_amorce": Decimal(1),
        }
        return Article.objects.create(**{**defauts, **kwargs})

    def _annote(self, article):
        return Article.objects.avec_besoin().get(pk=article.pk)

    def test_stock_estime_annotation_egale_property(self):
        article = self._article()
        annote = self._annote(article)
        self.assertAlmostEqual(
            annote.stock_estime_calc, float(article.stock_estime), places=2
        )

    def test_stock_estime_annotation_egale_property_avec_estimation_apprise(self):
        article = self._article(conso_par_jour_estimee=Decimal(2))
        annote = self._annote(article)
        self.assertAlmostEqual(
            annote.stock_estime_calc, float(article.stock_estime), places=2
        )

    def test_stock_estime_annotation_egale_property_sans_suivi_auto(self):
        article = self._article(suivi_auto=False)
        annote = self._annote(article)
        self.assertAlmostEqual(
            annote.stock_estime_calc, float(article.stock_estime), places=2
        )

    def test_besoin_est_max_cible_moins_stock_estime(self):
        # stock_cible=40, stock_estime≈30 (10 jours à 1/jour) → besoin≈10.
        article = self._article()
        annote = self._annote(article)
        self.assertAlmostEqual(annote.besoin, 10.0, places=1)

    def test_besoin_nul_quand_stock_suffisant(self):
        article = self._article(stock_cible=Decimal(2), suivi_auto=False)
        annote = self._annote(article)
        self.assertEqual(annote.besoin, 0.0)

    def test_besoin_inclut_les_demandes_ponctuelles_non_satisfaites(self):
        user = User.objects.create_user("smoke_besoin_ponctuel")
        article = self._article(stock_cible=Decimal(0), stock_reference=Decimal(0))
        DemandePonctuelle.objects.create(
            article=article, profil=user.profil, quantite=Decimal(2)
        )
        annote = self._annote(article)
        self.assertEqual(annote.besoin, 2.0)

    def test_demande_satisfaite_exclue_du_besoin(self):
        user = User.objects.create_user("smoke_besoin_satisfait")
        article = self._article(stock_cible=Decimal(0), stock_reference=Decimal(0))
        sortie = Sortie.objects.create(foyer=self.foyer, cree_par=user.profil)
        ligne = Ligne.objects.create(sortie=sortie, article=article)
        DemandePonctuelle.objects.create(
            article=article,
            profil=user.profil,
            quantite=Decimal(2),
            satisfaite_par=ligne,
        )
        annote = self._annote(article)
        self.assertEqual(annote.besoin, 0.0)

    def test_articles_sans_rayon_apres_ceux_avec_rayon(self):
        """§9 : les articles sans rayon se regroupent EN FIN de liste, pas au début."""
        from django.db.models import F

        rayon = Rayon.objects.create(foyer=self.foyer, nom="Fruits", ordre=1)
        sans_rayon = self._article(nom="Sans rayon")
        avec_rayon = self._article(nom="Avec rayon", rayon=rayon)
        noms = list(
            Article.objects.filter(foyer=self.foyer)
            .order_by(F("rayon__ordre").asc(nulls_last=True), "nom")
            .values_list("nom", flat=True)
        )
        self.assertEqual(noms.index(avec_rayon.nom), 0)
        self.assertEqual(noms.index(sans_rayon.nom), len(noms) - 1)


class CoursesViewsSmokeTest(TestCase):
    """Vues serveur de la phase 1 (§11) : À acheter / Inventaire / Historique."""

    def setUp(self):
        self.user = User.objects.create_user("smoke_courses_vues", password="x")
        self.profil = self.user.profil
        self.foyer = Foyer.objects.create(nom="Foyer vues")
        self.foyer.membres.add(self.profil)
        self.rayon = Rayon.objects.create(foyer=self.foyer, nom="Fruits", ordre=1)
        self.article = Article.objects.create(
            foyer=self.foyer,
            nom="Bananes",
            rayon=self.rayon,
            stock_cible=Decimal(3),
            stock_reference=Decimal(0),
        )
        self.client.force_login(self.user)

    def test_mes_foyers_redirige_si_un_seul_foyer(self):
        r = self.client.get(url("courses:mes-foyers"))
        self.assertRedirects(
            r, url("courses:a-acheter", self.foyer.slug), fetch_redirect_response=False
        )

    def test_mes_foyers_liste_si_plusieurs_foyers(self):
        autre = Foyer.objects.create(nom="Autre foyer")
        autre.membres.add(self.profil)
        r = self.client.get(url("courses:mes-foyers"))
        self.assertEqual(r.status_code, 200)

    def test_a_acheter_status_200(self):
        r = self.client.get(url("courses:a-acheter", self.foyer.slug))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Bananes")

    def test_inventaire_status_200(self):
        r = self.client.get(url("courses:inventaire", self.foyer.slug))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Bananes")

    def test_inventaire_regroupe_par_rayon(self):
        """Retour utilisateur : les rayons doivent apparaître en sections."""
        sans_rayon = Article.objects.create(foyer=self.foyer, nom="Sans rayon")
        r = self.client.get(url("courses:inventaire", self.foyer.slug))
        self.assertContains(r, "data-rayon-section", count=2)  # Fruits + Sans rayon
        self.assertContains(r, sans_rayon.nom)

    def test_inventaire_recherche_texte_inclut_rayon_et_etiquette(self):
        """Retour utilisateur : la recherche doit matcher le rayon ou l'étiquette,
        pas seulement le nom — vérifié via l'attribut data-recherche précalculé."""
        etiquette = Etiquette.objects.create(foyer=self.foyer, nom="Bio")
        self.article.etiquettes.add(etiquette)
        r = self.client.get(url("courses:inventaire", self.foyer.slug))
        content = r.content.decode()
        debut = content.index(f'id="a-{self.article.pk}"')
        extrait = content[debut : debut + 400]
        self.assertIn("fruits", extrait.lower())
        self.assertIn("bio", extrait.lower())

    def test_historique_status_200(self):
        r = self.client.get(url("courses:historique", self.foyer.slug))
        self.assertEqual(r.status_code, 200)

    def test_foyer_d_un_autre_profil_est_inaccessible(self):
        """Le scoping par `request.user.profil.foyers` doit isoler les foyers entre eux."""
        autre_foyer = Foyer.objects.create(nom="Pas le mien")
        r = self.client.get(url("courses:a-acheter", autre_foyer.slug))
        self.assertEqual(r.status_code, 404)

    def _sortie_par_defaut(self):
        return Sortie.objects.get(foyer=self.foyer, nom="")

    def test_toggle_ligne_cree_et_coche(self):
        self.client.get(
            url("courses:a-acheter", self.foyer.slug)
        )  # crée la sortie par défaut
        sortie = self._sortie_par_defaut()
        r = self.client.post(
            url("courses:toggle-ligne", self.foyer.slug, sortie.pk, self.article.pk),
            {"quantite": "3"},
        )
        self.assertEqual(r.status_code, 302)
        ligne = Ligne.objects.get(sortie=sortie, article=self.article)
        self.assertEqual(ligne.quantite, Decimal("3"))
        self.assertIsNotNone(ligne.cochee_le)

        # un second appel décoche (toggle)
        self.client.post(
            url("courses:toggle-ligne", self.foyer.slug, sortie.pk, self.article.pk)
        )
        ligne.refresh_from_db()
        self.assertIsNone(ligne.cochee_le)

    def test_modifier_quantite_ligne(self):
        """« Il ne restait que 6 œufs, pas 12 » — la quantité reste éditable après coche."""
        self.client.get(url("courses:a-acheter", self.foyer.slug))
        sortie = self._sortie_par_defaut()
        self.client.post(
            url("courses:toggle-ligne", self.foyer.slug, sortie.pk, self.article.pk),
            {"quantite": "12"},
        )
        r = self.client.post(
            url(
                "courses:modifier-quantite-ligne",
                self.foyer.slug,
                sortie.pk,
                self.article.pk,
            ),
            {"quantite": "6"},
        )
        self.assertEqual(r.status_code, 302)
        ligne = Ligne.objects.get(sortie=sortie, article=self.article)
        self.assertEqual(ligne.quantite, Decimal("6"))

    def test_toggle_ligne_signale_sans_dupliquer_si_deja_dans_une_autre_sortie_ouverte(
        self,
    ):
        """§5.1 : fusion douce — on signale, on ne crée jamais de doublon d'article ouvert."""
        self.client.get(url("courses:a-acheter", self.foyer.slug))
        sortie_defaut = self._sortie_par_defaut()
        sortie_apero = Sortie.objects.create(
            foyer=self.foyer, nom="Apéro", cree_par=self.profil
        )
        Ligne.objects.create(sortie=sortie_apero, article=self.article)

        r = self.client.post(
            url(
                "courses:toggle-ligne",
                self.foyer.slug,
                sortie_defaut.pk,
                self.article.pk,
            ),
            {"quantite": "1"},
            follow=True,
        )
        self.assertFalse(
            Ligne.objects.filter(sortie=sortie_defaut, article=self.article).exists()
        )
        messages = [str(m) for m in r.context[0]["messages"]]
        self.assertTrue(any("Apéro" in m for m in messages))

    def test_valider_sortie_cree_mouvement_et_met_a_jour_le_stock(self):
        self.client.get(url("courses:a-acheter", self.foyer.slug))
        sortie = self._sortie_par_defaut()
        self.client.post(
            url("courses:toggle-ligne", self.foyer.slug, sortie.pk, self.article.pk),
            {"quantite": "3"},
        )
        r = self.client.post(url("courses:valider-sortie", self.foyer.slug, sortie.pk))
        self.assertEqual(r.status_code, 302)

        self.article.refresh_from_db()
        self.assertEqual(self.article.stock_reference, Decimal("3"))
        self.assertIsNotNone(self.article.stock_maj_le)
        mouvement = MouvementStock.objects.get(article=self.article)
        self.assertEqual(mouvement.type, MouvementStock.Type.ACHAT)
        self.assertEqual(mouvement.quantite, Decimal("3"))

        sortie.refresh_from_db()
        self.assertIsNotNone(sortie.cloture_le)

    def test_recompter_cree_un_mouvement_de_recalage(self):
        r = self.client.post(
            url("courses:recompter", self.foyer.slug, self.article.pk),
            {"nouvelle_valeur": "12"},
        )
        self.assertEqual(r.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.stock_reference, Decimal("12"))
        mouvement = MouvementStock.objects.get(article=self.article)
        self.assertEqual(mouvement.type, MouvementStock.Type.RECALAGE)
        self.assertEqual(mouvement.quantite, Decimal("12"))

    def _post_ajax(self, view_name, *args, data=None):
        return self.client.post(
            url(view_name, *args), data or {}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

    def test_modifier_cible_ajax_renvoie_un_etat_json_sans_rediriger(self):
        """Retour utilisateur : un aller-retour AJAX ne doit pas recharger la page —
        sinon on perd la position de scroll et l'état d'ouverture des autres articles."""
        r = self._post_ajax(
            "courses:article-cible",
            self.foyer.slug,
            self.article.pk,
            data={"delta": "2"},
        )
        self.assertEqual(r.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.stock_cible, Decimal("5"))
        data = r.json()
        self.assertEqual(data["stock_cible"], "5")
        self.assertIn("besoin", data)
        self.assertIn("pct", data)

    def test_modifier_ponctuel_ajax(self):
        r = self._post_ajax(
            "courses:article-ponctuel",
            self.foyer.slug,
            self.article.pk,
            data={"delta": "3"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["ponctuel"], "3")

    def test_recompter_ajax(self):
        r = self._post_ajax(
            "courses:recompter",
            self.foyer.slug,
            self.article.pk,
            data={"nouvelle_valeur": "7"},
        )
        self.assertEqual(r.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.stock_reference, Decimal("7"))
        self.assertEqual(r.json()["stock_estime"], "7,0")

    def test_recompter_ajax_invalide_renvoie_400(self):
        r = self._post_ajax(
            "courses:recompter",
            self.foyer.slug,
            self.article.pk,
            data={"nouvelle_valeur": "pas-un-nombre"},
        )
        self.assertEqual(r.status_code, 400)

    def test_creer_etiquette_ajax(self):
        """Création à la volée depuis Tom Select (fiche article) — cf. conception.md §6.3."""
        r = self.client.post(
            url("courses:creer-etiquette", self.foyer.slug),
            data=json.dumps({"nom": "Bio"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        etiquette = Etiquette.objects.get(foyer=self.foyer, nom="Bio")
        self.assertEqual(data, {"id": etiquette.pk, "nom": "Bio"})

    def test_creer_etiquette_ajax_idempotent(self):
        r1 = self.client.post(
            url("courses:creer-etiquette", self.foyer.slug),
            data=json.dumps({"nom": "Apéro"}),
            content_type="application/json",
        )
        r2 = self.client.post(
            url("courses:creer-etiquette", self.foyer.slug),
            data=json.dumps({"nom": "Apéro"}),
            content_type="application/json",
        )
        self.assertEqual(r1.json()["id"], r2.json()["id"])
        self.assertEqual(
            Etiquette.objects.filter(foyer=self.foyer, nom="Apéro").count(), 1
        )

    def test_creer_etiquette_ajax_nom_vide_rejete(self):
        r = self.client.post(
            url("courses:creer-etiquette", self.foyer.slug),
            data=json.dumps({"nom": "   "}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_creer_rayon_ajax(self):
        """Création à la volée depuis Tom Select (fiche article)."""
        r = self.client.post(
            url("courses:creer-rayon", self.foyer.slug),
            data=json.dumps({"nom": "Surgelés"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        rayon = Rayon.objects.get(foyer=self.foyer, nom="Surgelés")
        self.assertEqual(r.json(), {"id": rayon.pk, "nom": "Surgelés"})

    def test_creer_rayon_ajax_atterrit_en_fin_de_liste(self):
        """L'ordre compte pour le parcours magasin — pas de collision à ordre=0."""
        r = self.client.post(
            url("courses:creer-rayon", self.foyer.slug),
            data=json.dumps({"nom": "Surgelés"}),
            content_type="application/json",
        )
        rayon = Rayon.objects.get(pk=r.json()["id"])
        self.assertGreater(rayon.ordre, self.rayon.ordre)

    def test_creer_rayon_ajax_idempotent(self):
        r1 = self.client.post(
            url("courses:creer-rayon", self.foyer.slug),
            data=json.dumps({"nom": "Surgelés"}),
            content_type="application/json",
        )
        r2 = self.client.post(
            url("courses:creer-rayon", self.foyer.slug),
            data=json.dumps({"nom": "Surgelés"}),
            content_type="application/json",
        )
        self.assertEqual(r1.json()["id"], r2.json()["id"])
        self.assertEqual(
            Rayon.objects.filter(foyer=self.foyer, nom="Surgelés").count(), 1
        )

    def test_creer_rayon_ajax_nom_vide_rejete(self):
        r = self.client.post(
            url("courses:creer-rayon", self.foyer.slug),
            data=json.dumps({"nom": "   "}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)

    def test_corriger_sortie_defait_le_mouvement_d_achat(self):
        self.client.get(url("courses:a-acheter", self.foyer.slug))
        sortie = self._sortie_par_defaut()
        self.client.post(
            url("courses:toggle-ligne", self.foyer.slug, sortie.pk, self.article.pk),
            {"quantite": "3"},
        )
        self.client.post(url("courses:valider-sortie", self.foyer.slug, sortie.pk))

        r = self.client.post(url("courses:corriger-sortie", self.foyer.slug, sortie.pk))
        self.assertEqual(r.status_code, 302)

        self.article.refresh_from_db()
        self.assertEqual(self.article.stock_reference, Decimal("0"))
        self.assertFalse(MouvementStock.objects.filter(article=self.article).exists())
        sortie.refresh_from_db()
        self.assertIsNone(sortie.cloture_le)
