from django.urls import path
from django.utils.translation import gettext_lazy as _

from courses import views

app_name = "courses"

urlpatterns = [
    path("", views.mes_foyers, name="mes-foyers"),
    path("<slug:foyer_slug>/", views.vue_a_acheter, name="a-acheter"),
    path(
        _("<slug:foyer_slug>/sortie/nouvelle/"),
        views.creer_sortie,
        name="creer-sortie",
    ),
    path(
        _("<slug:foyer_slug>/sortie/<int:sortie_id>/article/<int:article_id>/toggle/"),
        views.toggle_ligne,
        name="toggle-ligne",
    ),
    path(
        _(
            "<slug:foyer_slug>/sortie/<int:sortie_id>/article/<int:article_id>/indisponible/"
        ),
        views.toggle_indisponible,
        name="toggle-indisponible",
    ),
    path(
        _(
            "<slug:foyer_slug>/sortie/<int:sortie_id>/article/<int:article_id>/quantite/"
        ),
        views.modifier_quantite_ligne,
        name="modifier-quantite-ligne",
    ),
    path(
        _("<slug:foyer_slug>/sortie/<int:sortie_id>/ajouter/"),
        views.ajouter_article,
        name="ajouter-article",
    ),
    path(
        _("<slug:foyer_slug>/sortie/<int:sortie_id>/valider/"),
        views.valider_sortie,
        name="valider-sortie",
    ),
    path(_("<slug:foyer_slug>/inventaire/"), views.vue_inventaire, name="inventaire"),
    path(
        _("<slug:foyer_slug>/inventaire/nouveau/"),
        views.creer_article,
        name="creer-article",
    ),
    path(
        _("<slug:foyer_slug>/inventaire/<int:article_id>/modifier/"),
        views.modifier_article,
        name="modifier-article",
    ),
    path(
        _("<slug:foyer_slug>/etiquettes/creer/"),
        views.creer_etiquette,
        name="creer-etiquette",
    ),
    path(
        _("<slug:foyer_slug>/rayons/creer/"),
        views.creer_rayon,
        name="creer-rayon",
    ),
    path(
        _("<slug:foyer_slug>/inventaire/<int:article_id>/cible/"),
        views.modifier_cible,
        name="article-cible",
    ),
    path(
        _("<slug:foyer_slug>/inventaire/<int:article_id>/ponctuel/"),
        views.modifier_ponctuel,
        name="article-ponctuel",
    ),
    path(
        _("<slug:foyer_slug>/inventaire/<int:article_id>/recompter/"),
        views.recompter,
        name="recompter",
    ),
    path(_("<slug:foyer_slug>/historique/"), views.vue_historique, name="historique"),
    path(
        _("<slug:foyer_slug>/historique/<int:sortie_id>/corriger/"),
        views.corriger_sortie,
        name="corriger-sortie",
    ),
]
