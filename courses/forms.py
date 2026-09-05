from decimal import Decimal

from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.widgets import TomSelectMultipleWidget, TomSelectWidget
from courses.models import Article, Magasin, Rayon, Sortie


class ArticleForm(forms.ModelForm):
    """Fiche article (conception.md §6.4/§9) : `rayon` et `etiquettes` restent facultatifs à la
    création — un article importé ou saisi vite ne doit coûter qu'un nom (§9 étape 3)."""

    class Meta:
        model = Article
        fields = (
            "nom",
            "rayon",
            "etiquettes",
            "unite",
            "conditionnement",
            "stock_cible",
            "suivi_auto",
            "conso_amorce",
            "note",
        )
        widgets = {
            "rayon": TomSelectWidget(placeholder=_("Rayon")),
            "etiquettes": TomSelectMultipleWidget(placeholder=_("Étiquettes")),
        }
        help_texts = {
            "conso_amorce": _(
                "Graine de démarrage — utile pour amorcer le suivi avant d'avoir assez "
                "d'historique. Devient inerte dès que la consommation est apprise."
            ),
        }

    def __init__(self, *args, foyer=None, **kwargs):
        self.foyer = foyer
        super().__init__(*args, **kwargs)
        foyer = foyer or getattr(self.instance, "foyer", None)
        self.fields["rayon"].queryset = Rayon.objects.filter(foyer=foyer)
        self.fields["etiquettes"].queryset = self.fields["etiquettes"].queryset.filter(
            foyer=foyer
        )
        if foyer:
            # Création à la volée (Tom Select `create`) pour les deux champs référentiel.
            self.fields["etiquettes"].widget.create_url = reverse(
                "courses:creer-etiquette", kwargs={"foyer_slug": foyer.slug}
            )
            self.fields["rayon"].widget.create_url = reverse(
                "courses:creer-rayon", kwargs={"foyer_slug": foyer.slug}
            )

    def save(self, commit=True):
        self.instance.foyer = self.foyer or self.instance.foyer
        return super().save(commit=commit)


class SortieForm(forms.ModelForm):
    """Ouverture d'une sortie nommée (§5.1) — « Apéro samedi », en parallèle de la sortie
    courante qui porte le besoin global."""

    class Meta:
        model = Sortie
        fields = ("nom", "magasin")
        widgets = {"magasin": TomSelectWidget(placeholder=_("Magasin (optionnel)"))}

    def __init__(self, *args, foyer=None, **kwargs):
        self.foyer = foyer
        super().__init__(*args, **kwargs)
        self.fields["nom"].required = True
        self.fields["magasin"].queryset = Magasin.objects.filter(
            foyer=foyer, actif=True
        )


class AjouterArticleForm(forms.Form):
    """Ajoute un article existant du catalogue à une sortie (vue magasin déjà entamée)."""

    article = forms.ModelChoiceField(
        queryset=Article.objects.none(),
        widget=TomSelectWidget(placeholder=_("Article")),
    )
    quantite = forms.DecimalField(
        max_digits=9,
        decimal_places=3,
        initial=Decimal(1),
        min_value=Decimal(0),
        label=_("Quantité"),
    )

    def __init__(self, *args, foyer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["article"].queryset = Article.objects.filter(
            foyer=foyer, actif=True
        ).order_by("nom")


class RecompterForm(forms.Form):
    """« Recompter » (§6.5) : le stock estimé n'est pas éditable directement — il se corrige
    par ce formulaire, qui écrit un `MouvementStock(type=recalage)`."""

    nouvelle_valeur = forms.DecimalField(
        max_digits=9, decimal_places=3, min_value=Decimal(0), label=_("Il en reste")
    )
    commentaire = forms.CharField(
        max_length=255, required=False, label=_("Commentaire")
    )
