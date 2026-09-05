import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Max, Value
from django.db.models.functions import Greatest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import floatformat
from django.utils import dateformat, timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django.views.decorators.http import require_POST

from courses.forms import AjouterArticleForm, ArticleForm, RecompterForm, SortieForm
from courses.models import (
    Article,
    DemandePonctuelle,
    Etiquette,
    Ligne,
    MouvementStock,
    Rayon,
    Sortie,
)


def _foyer_du_profil(request, foyer_slug):
    return get_object_or_404(request.user.profil.foyers, slug=foyer_slug, archive=False)


def _sortie_par_defaut(foyer, profil):
    """
    La sortie « courante », implicite : elle porte le besoin global (§5.1 — « Tout ce qui
    manque » n'est rattachée à AUCUNE sortie nommée), mais cocher un article doit bien
    persister quelque part. Une seule par foyer, sans nom, get-or-create.
    """
    sortie = (
        foyer.sorties.filter(cloture_le__isnull=True, nom="")
        .order_by("cree_le")
        .first()
    )
    if sortie is None:
        sortie = foyer.sorties.create(nom="", cree_par=profil)
    return sortie


def _decimal(valeur, defaut=Decimal(0)):
    try:
        return Decimal(valeur)
    except (InvalidOperation, TypeError):
        return defaut


# ---------------------------------------------------------------------------
# Foyers
# ---------------------------------------------------------------------------


@login_required
def mes_foyers(request):
    foyers = list(request.user.profil.foyers.filter(archive=False))
    if len(foyers) == 1:
        return redirect("courses:a-acheter", foyer_slug=foyers[0].slug)
    return render(request, "courses/foyers_liste.html", {"foyers": foyers})


# ---------------------------------------------------------------------------
# À acheter
# ---------------------------------------------------------------------------


@login_required
def vue_a_acheter(request, foyer_slug):
    foyer = _foyer_du_profil(request, foyer_slug)
    profil = request.user.profil
    sortie_courante = _sortie_par_defaut(foyer, profil)

    sorties_nommees = list(
        foyer.sorties.filter(cloture_le__isnull=True)
        .exclude(nom="")
        .order_by("cree_le")
    )

    sortie_id = request.GET.get("sortie")
    sortie_affichee = None
    if sortie_id:
        sortie_affichee = get_object_or_404(
            Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=True
        )

    if sortie_affichee is None:
        # Vue par défaut : le besoin global, calculé — pas une simple liste de Ligne (§4/§5.1).
        articles = (
            Article.objects.filter(foyer=foyer, actif=True)
            .avec_besoin()
            .filter(besoin__gt=0)
            .select_related("rayon")
            .order_by(F("rayon__ordre").asc(nulls_last=True), "nom")
        )
        lignes_par_article = {
            ligne.article_id: ligne
            for ligne in sortie_courante.lignes.select_related("cochee_par__user")
        }
        demandeurs_par_article = {}
        for demande in DemandePonctuelle.objects.filter(
            article__foyer=foyer, satisfaite_par__isnull=True
        ).select_related("profil__user"):
            demandeurs_par_article.setdefault(demande.article_id, []).append(
                demande.profil.user.username
            )
        rangees = [
            {
                "article": article,
                "ligne": lignes_par_article.get(article.id),
                "demandeurs": demandeurs_par_article.get(article.id, []),
                "quantite_defaut": article.besoin,
            }
            for article in articles
        ]
        sortie_pour_actions = sortie_courante
    else:
        lignes = sortie_affichee.lignes.select_related(
            "article", "article__rayon", "cochee_par__user"
        ).order_by(F("article__rayon__ordre").asc(nulls_last=True), "article__nom")
        rangees = [
            {
                "article": ligne.article,
                "ligne": ligne,
                "demandeurs": [],
                "quantite_defaut": ligne.quantite,
            }
            for ligne in lignes
        ]
        sortie_pour_actions = sortie_affichee

    rayons = _grouper_par_rayon(rangees)
    nb_coches = sum(1 for r in rangees if r["ligne"] and r["ligne"].cochee_le)

    context = {
        "foyer": foyer,
        "onglet": "acheter",
        "rayons": rayons,
        "nb_total": len(rangees),
        "nb_coches": nb_coches,
        "sortie_courante": sortie_courante,
        "sorties_nommees": sorties_nommees,
        "sortie_affichee": sortie_affichee,
        "sortie_pour_actions": sortie_pour_actions,
        "vue_globale": sortie_affichee is None,
        "sortie_form": SortieForm(foyer=foyer),
    }
    return render(request, "courses/a_acheter.html", context)


def _grouper_par_rayon(rangees):
    groupes = []
    groupe_courant = None
    for rangee in rangees:
        rayon = rangee["article"].rayon
        cle = rayon.id if rayon else None
        if groupe_courant is None or groupe_courant["cle"] != cle:
            groupe_courant = {"cle": cle, "rayon": rayon, "rangees": []}
            groupes.append(groupe_courant)
        groupe_courant["rangees"].append(rangee)
    return groupes


@login_required
@require_POST
def creer_sortie(request, foyer_slug):
    foyer = _foyer_du_profil(request, foyer_slug)
    form = SortieForm(request.POST, foyer=foyer)
    if form.is_valid():
        sortie = form.save(commit=False)
        sortie.foyer = foyer
        sortie.cree_par = request.user.profil
        sortie.save()
        messages.success(
            request, _("Sortie « %(sortie)s » ouverte.") % {"sortie": sortie}
        )
        return redirect(f"{_url_acheter(foyer)}?sortie={sortie.pk}")
    for erreur in form.errors.values():
        messages.error(request, erreur.as_text())
    return redirect(_url_acheter(foyer))


def _url_acheter(foyer):
    from django.urls import reverse

    return reverse("courses:a-acheter", kwargs={"foyer_slug": foyer.slug})


@login_required
@require_POST
def toggle_ligne(request, foyer_slug, sortie_id, article_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    sortie = get_object_or_404(
        Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=True
    )
    article = get_object_or_404(Article, pk=article_id, foyer=foyer)
    ligne = Ligne.objects.filter(sortie=sortie, article=article).first()

    if ligne:
        ligne.cochee_le = None if ligne.cochee_le else timezone.now()
        ligne.cochee_par = request.user.profil if ligne.cochee_le else ligne.cochee_par
        ligne.save(update_fields=["cochee_le", "cochee_par", "modifie_le"])
    else:
        conflit = (
            Ligne.objects.filter(
                article=article, sortie__foyer=foyer, sortie__cloture_le__isnull=True
            )
            .exclude(sortie=sortie)
            .select_related("sortie")
            .first()
        )
        if conflit:
            # §5.1 : on signale plutôt que de créer un doublon — fusion douce, pas de rejet.
            messages.warning(
                request,
                _(
                    "« %(article)s » est déjà dans « %(sortie)s ». Cochez-le depuis "
                    "cette sortie-là pour éviter de l'acheter deux fois."
                )
                % {"article": article, "sortie": conflit.sortie},
            )
        else:
            quantite = _decimal(request.POST.get("quantite"), Decimal(1)) or Decimal(1)
            Ligne.objects.create(
                sortie=sortie,
                article=article,
                quantite=quantite,
                cochee_le=timezone.now(),
                cochee_par=request.user.profil,
                origine=Ligne.Origine.SEUIL
                if sortie.nom == ""
                else Ligne.Origine.MANUEL,
            )

    return _redirect_vers_acheter(request, foyer, sortie)


@login_required
@require_POST
def modifier_quantite_ligne(request, foyer_slug, sortie_id, article_id):
    """
    Ajuste la quantité d'une Ligne déjà créée — ex. « il ne restait que 6 œufs en rayon,
    pas 12 ». La quantité de départ (besoin ou saisie manuelle) n'est qu'une proposition.
    """
    foyer = _foyer_du_profil(request, foyer_slug)
    sortie = get_object_or_404(
        Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=True
    )
    ligne = get_object_or_404(Ligne, sortie=sortie, article_id=article_id)
    quantite = _decimal(request.POST.get("quantite"), None)
    if quantite is not None and quantite >= 0:
        ligne.quantite = quantite
        ligne.save(update_fields=["quantite", "modifie_le"])
    return _redirect_vers_acheter(request, foyer, sortie)


@login_required
@require_POST
def toggle_indisponible(request, foyer_slug, sortie_id, article_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    sortie = get_object_or_404(
        Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=True
    )
    ligne = get_object_or_404(Ligne, sortie=sortie, article_id=article_id)
    if not ligne.cochee_le:  # « acheté » gagne toujours (§5)
        ligne.indisponible_le = None if ligne.indisponible_le else timezone.now()
        ligne.save(update_fields=["indisponible_le", "modifie_le"])
    return _redirect_vers_acheter(request, foyer, sortie)


def _redirect_vers_acheter(request, foyer, sortie):
    url = _url_acheter(foyer)
    if sortie.nom:
        url = f"{url}?sortie={sortie.pk}"
    return redirect(request.META.get("HTTP_REFERER") or url)


@login_required
def ajouter_article(request, foyer_slug, sortie_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    sortie = get_object_or_404(
        Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=True
    )
    form = AjouterArticleForm(request.POST or None, foyer=foyer)
    if request.method == "POST" and form.is_valid():
        article = form.cleaned_data["article"]
        Ligne.objects.get_or_create(
            sortie=sortie,
            article=article,
            defaults={"quantite": form.cleaned_data["quantite"]},
        )
        return redirect(f"{_url_acheter(foyer)}?sortie={sortie.pk}")
    return render(
        request,
        "courses/ajouter_article.html",
        {"foyer": foyer, "sortie": sortie, "form": form},
    )


@login_required
@require_POST
@transaction.atomic
def valider_sortie(request, foyer_slug, sortie_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    sortie = get_object_or_404(
        Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=True
    )
    maintenant = timezone.now()

    lignes_achetees = list(
        sortie.lignes.filter(
            cochee_le__isnull=False, indisponible_le__isnull=True
        ).select_related("article")
    )
    for ligne in lignes_achetees:
        MouvementStock.objects.create(
            article=ligne.article,
            type=MouvementStock.Type.ACHAT,
            ligne=ligne,
            quantite=ligne.quantite,
            date=maintenant,
            profil=request.user.profil,
        )
        Article.objects.filter(pk=ligne.article_id).update(
            stock_reference=F("stock_reference") + ligne.quantite,
            stock_maj_le=maintenant,
        )
        # Un achat couvre les demandes en attente sur cet article — la trace reste (§5).
        DemandePonctuelle.objects.filter(
            article=ligne.article, satisfaite_par__isnull=True
        ).update(satisfaite_par=ligne)

    sortie.cloture_le = maintenant
    sortie.save(update_fields=["cloture_le"])

    nb_lignes = len(lignes_achetees)
    texte = ngettext_lazy(
        "%(nb)d article validé — stock mis à jour.",
        "%(nb)d articles validés — stock mis à jour.",
        nb_lignes,
    ) % {"nb": nb_lignes}
    messages.success(request, texte)
    return redirect(_url_acheter(foyer))


# ---------------------------------------------------------------------------
# Inventaire
# ---------------------------------------------------------------------------


def _formate_quantite(valeur):
    """
    Même filtre que le template (`floatformat:"-3"`) — sensible à la locale (virgule en
    français). Utilisé aussi bien à l'affichage initial que dans les réponses JSON des
    steppers, pour qu'une valeur mise à jour en AJAX ait le même rendu que l'original.
    """
    return floatformat(valeur, "-3") or "0"


def _estimation_label(article):
    """
    Motif recalculé à l'affichage, jamais stocké (§12 de conception.md) — sinon il deviendrait
    faux en silence dès que l'historique change.
    """
    if not article.suivi_auto:
        return _("Suivi automatique désactivé")
    if article.conso_par_jour_estimee:
        return _("≈ %(taux)s / jour (estimé)") % {
            "taux": _formate_quantite(article.conso_par_jour_estimee)
        }
    if article.conso_amorce:
        return _("≈ %(taux)s / jour (amorce, pas encore d'historique)") % {
            "taux": _formate_quantite(article.conso_amorce)
        }
    return _("Pas assez d'historique pour estimer")


def _grouper_articles_par_rayon(articles):
    groupes = []
    groupe_courant = None
    for article in articles:
        cle = article.rayon_id
        if groupe_courant is None or groupe_courant["cle"] != cle:
            groupe_courant = {"cle": cle, "rayon": article.rayon, "articles": []}
            groupes.append(groupe_courant)
        groupe_courant["articles"].append(article)
    return groupes


@login_required
def vue_inventaire(request, foyer_slug):
    foyer = _foyer_du_profil(request, foyer_slug)
    ouvert_id = request.GET.get("ouvert")

    articles = list(
        Article.objects.filter(foyer=foyer, actif=True)
        .avec_besoin()
        .select_related("rayon")
        .prefetch_related("etiquettes")
        .order_by(F("rayon__ordre").asc(nulls_last=True), "nom")
    )

    profil = request.user.profil
    demandes = DemandePonctuelle.objects.filter(
        article__foyer=foyer, profil=profil, satisfaite_par__isnull=True
    )
    ponctuel_par_article = {d.article_id: d.quantite for d in demandes}

    for article in articles:
        article.ponctuel_personnel = ponctuel_par_article.get(article.id, Decimal(0))
        article.estimation_label = _estimation_label(article)
        # Filtre côté client (JS, cf. courses/static/courses/js/inventaire-filtre.js) :
        # match sur le nom, le rayon ou les étiquettes — précalculé pour éviter de
        # ré-implémenter la même logique de recherche en JS.
        mots = [article.nom, article.rayon.nom if article.rayon else ""]
        mots += [etiquette.nom for etiquette in article.etiquettes.all()]
        article.recherche_texte = " ".join(mots).lower()

    sans_rayon = Article.objects.filter(
        foyer=foyer, actif=True, rayon__isnull=True
    ).count()

    context = {
        "foyer": foyer,
        "onglet": "inventaire",
        "rayons": _grouper_articles_par_rayon(articles),
        "ouvert_id": ouvert_id,
        "sans_rayon": sans_rayon,
    }
    return render(request, "courses/inventaire.html", context)


def _url_inventaire(foyer, article_id):
    from django.urls import reverse

    url = reverse("courses:inventaire", kwargs={"foyer_slug": foyer.slug})
    return f"{url}?ouvert={article_id}#a-{article_id}"


def _est_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _etat_article_json(article_id, profil):
    """
    Réponse JSON commune aux trois actions de l'Inventaire (cible/ponctuel/recompter) :
    un aller-retour serveur par tape de +/- perdrait sinon la position de scroll et
    l'état d'ouverture des autres articles (retour utilisateur). Le JS met juste à
    jour les quelques éléments concernés — pas de rechargement de page.
    """
    article = Article.objects.avec_besoin().get(pk=article_id)
    pct = 0
    if article.stock_cible_f:
        pct = max(
            0, min(100, round(article.stock_estime_calc / article.stock_cible_f * 100))
        )
    demande = DemandePonctuelle.objects.filter(
        article_id=article_id,
        profil=profil,
        sortie__isnull=True,
        satisfaite_par__isnull=True,
    ).first()
    return JsonResponse(
        {
            "stock_cible": _formate_quantite(article.stock_cible),
            "ponctuel": _formate_quantite(demande.quantite if demande else Decimal(0)),
            "besoin": _formate_quantite(article.besoin) if article.besoin else 0,
            "pct": pct,
            "stock_estime": floatformat(article.stock_estime_calc, 1),
        }
    )


@login_required
@require_POST
def modifier_cible(request, foyer_slug, article_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    article = get_object_or_404(Article, pk=article_id, foyer=foyer)
    delta = _decimal(request.POST.get("delta"))
    Article.objects.filter(pk=article.pk).update(
        stock_cible=Greatest(F("stock_cible") + delta, Value(Decimal(0)))
    )
    if _est_ajax(request):
        return _etat_article_json(article.pk, request.user.profil)
    return redirect(_url_inventaire(foyer, article.pk))


@login_required
@require_POST
def modifier_ponctuel(request, foyer_slug, article_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    article = get_object_or_404(Article, pk=article_id, foyer=foyer)
    profil = request.user.profil
    delta = _decimal(request.POST.get("delta"))

    demande = DemandePonctuelle.objects.filter(
        article=article, profil=profil, sortie__isnull=True, satisfaite_par__isnull=True
    ).first()
    nouvelle_quantite = (demande.quantite if demande else Decimal(0)) + delta

    if nouvelle_quantite <= 0:
        if demande:
            demande.delete()
    elif demande:
        demande.quantite = nouvelle_quantite
        demande.save(update_fields=["quantite", "modifie_le"])
    else:
        DemandePonctuelle.objects.create(
            article=article, profil=profil, quantite=nouvelle_quantite
        )

    if _est_ajax(request):
        return _etat_article_json(article.pk, profil)
    return redirect(_url_inventaire(foyer, article.pk))


@login_required
@require_POST
@transaction.atomic
def recompter(request, foyer_slug, article_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    article = get_object_or_404(Article, pk=article_id, foyer=foyer)
    form = RecompterForm(request.POST)
    if form.is_valid():
        nouvelle_valeur = form.cleaned_data["nouvelle_valeur"]
        maintenant = timezone.now()
        MouvementStock.objects.create(
            article=article,
            type=MouvementStock.Type.RECALAGE,
            quantite=nouvelle_valeur,
            date=maintenant,
            profil=request.user.profil,
            commentaire=form.cleaned_data["commentaire"],
        )
        Article.objects.filter(pk=article.pk).update(
            stock_reference=nouvelle_valeur, stock_maj_le=maintenant
        )
        if _est_ajax(request):
            return _etat_article_json(article.pk, request.user.profil)
        messages.success(
            request,
            _("Stock de « %(article)s » recompté : %(valeur)s.")
            % {"article": article, "valeur": nouvelle_valeur},
        )
    else:
        message_erreur = _("Valeur de recomptage invalide.")
        if _est_ajax(request):
            return JsonResponse({"error": str(message_erreur)}, status=400)
        messages.error(request, message_erreur)
    return redirect(_url_inventaire(foyer, article.pk))


@login_required
def creer_article(request, foyer_slug):
    foyer = _foyer_du_profil(request, foyer_slug)
    form = ArticleForm(request.POST or None, foyer=foyer)
    if request.method == "POST" and form.is_valid():
        article = form.save()
        messages.success(request, _("« %(article)s » créé.") % {"article": article})
        return redirect(_url_inventaire(foyer, article.pk))
    return render(
        request,
        "courses/article_form.html",
        {"foyer": foyer, "form": form, "article": None},
    )


@login_required
def modifier_article(request, foyer_slug, article_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    article = get_object_or_404(Article, pk=article_id, foyer=foyer)
    form = ArticleForm(request.POST or None, instance=article, foyer=foyer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request, _("« %(article)s » mis à jour.") % {"article": article}
        )
        return redirect(_url_inventaire(foyer, article.pk))
    return render(
        request,
        "courses/article_form.html",
        {"foyer": foyer, "form": form, "article": article},
    )


def _lire_nom_json(request, max_length):
    """Parse `{"nom": "..."}` depuis le corps JSON d'une requête Tom Select `create`."""
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return None, JsonResponse({"error": str(_("JSON invalide."))}, status=400)

    nom = str(payload.get("nom", "")).strip()
    if not nom or len(nom) > max_length:
        return None, JsonResponse({"error": str(_("Nom invalide."))}, status=400)
    return nom, None


@login_required
@require_POST
def creer_etiquette(request, foyer_slug):
    """
    Création à la volée depuis Tom Select (fiche article) — cf. conception.md §6.3.
    `get_or_create` : deux personnes qui tapent la même étiquette ne doivent pas se
    marcher dessus (unique_together foyer/nom), comme au §7.1 pour la synchro.
    """
    foyer = _foyer_du_profil(request, foyer_slug)
    nom, erreur = _lire_nom_json(request, max_length=50)
    if erreur:
        return erreur

    etiquette, _created = Etiquette.objects.get_or_create(foyer=foyer, nom=nom)
    return JsonResponse({"id": etiquette.pk, "nom": etiquette.nom})


@login_required
@require_POST
def creer_rayon(request, foyer_slug):
    """
    Création à la volée depuis Tom Select (fiche article). Contrairement à Etiquette,
    l'ordre compte ici (parcours du magasin, §5) : un nouveau rayon atterrit en FIN de
    liste par défaut plutôt qu'à `ordre=0`, sinon il doublerait le premier rayon existant.
    """
    foyer = _foyer_du_profil(request, foyer_slug)
    nom, erreur = _lire_nom_json(request, max_length=100)
    if erreur:
        return erreur

    rayon = Rayon.objects.filter(foyer=foyer, nom=nom).first()
    if rayon is None:
        ordre_max = (
            Rayon.objects.filter(foyer=foyer).aggregate(m=Max("ordre"))["m"] or 0
        )
        rayon = Rayon.objects.create(foyer=foyer, nom=nom, ordre=ordre_max + 1)
    return JsonResponse({"id": rayon.pk, "nom": rayon.nom})


# ---------------------------------------------------------------------------
# Historique
# ---------------------------------------------------------------------------


@login_required
def vue_historique(request, foyer_slug):
    foyer = _foyer_du_profil(request, foyer_slug)

    sorties_ouvertes = list(
        foyer.sorties.filter(cloture_le__isnull=True)
        .select_related("magasin")
        .prefetch_related("lignes__article")
        .order_by("cree_le")
    )
    sorties_closes = list(
        foyer.sorties.filter(cloture_le__isnull=False)
        .select_related("magasin", "cree_par__user")
        .prefetch_related("lignes__article")
        .order_by("-cloture_le")
    )
    for sortie in sorties_closes:
        sortie.mois_label = dateformat.format(sortie.cloture_le, "F Y")

    context = {
        "foyer": foyer,
        "onglet": "historique",
        "sorties_ouvertes": sorties_ouvertes,
        "sorties_closes": sorties_closes,
    }
    return render(request, "courses/historique.html", context)


@login_required
@require_POST
@transaction.atomic
def corriger_sortie(request, foyer_slug, sortie_id):
    foyer = _foyer_du_profil(request, foyer_slug)
    sortie = get_object_or_404(
        Sortie, pk=sortie_id, foyer=foyer, cloture_le__isnull=False
    )

    mouvements = MouvementStock.objects.filter(
        ligne__sortie=sortie, type=MouvementStock.Type.ACHAT
    )
    for mouvement in mouvements:
        Article.objects.filter(pk=mouvement.article_id).update(
            stock_reference=Greatest(
                F("stock_reference") - mouvement.quantite, Value(Decimal(0))
            )
        )
    DemandePonctuelle.objects.filter(satisfaite_par__sortie=sortie).update(
        satisfaite_par=None
    )
    mouvements.delete()

    sortie.cloture_le = None
    sortie.save(update_fields=["cloture_le"])
    messages.success(
        request,
        _("Sortie « %(sortie)s » rouverte — reprenez-la depuis « À acheter ».")
        % {"sortie": sortie},
    )
    return redirect(
        f"{_url_acheter(foyer)}?sortie={sortie.pk}"
        if sortie.nom
        else _url_acheter(foyer)
    )
