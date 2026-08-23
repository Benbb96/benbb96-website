"""
Tests de smoke
==============
Filet de sécurité de non-régression. Couvre :
  1. Status 200 des vues publiques clés
  2. Redirect (302) des vues login_required sans auth
  3. Non-régression des endpoints API tracker & super_moite_moite
  4. Obtention/rafraîchissement de token JWT
  5. Validité des `profil_lookup` des admins scopés (base.admin.ProfilScopedAdmin)
  6. Squelette de l'app courses (phase 0) : contraintes de modèles et seed_foyer

Lancer : python manage.py test smoke_tests
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone, translation
from rest_framework import status
from rest_framework.test import APIClient

from courses.models import Article, Etiquette, Foyer, Ligne, Rayon, Sortie


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
# 6. App courses (phase 0) — modèles et seed_foyer
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

    def test_etiquette_recreation_apres_soft_delete(self):
        """Soft delete + unicité (§5) : la contrainte est conditionnelle, pas unique_together."""
        etiquette = Etiquette.objects.create(foyer=self.foyer, nom="Apéro")
        etiquette.supprime_le = timezone.now()
        etiquette.save()
        # Ne doit pas lever IntegrityError malgré le même (foyer, nom).
        Etiquette.objects.create(foyer=self.foyer, nom="Apéro")

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

    def test_seed_foyer_slug_inconnu(self):
        with self.assertRaises(CommandError):
            call_command("seed_foyer", "slug-qui-nexiste-pas")
