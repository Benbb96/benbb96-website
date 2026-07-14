"""Widgets de sélection « searchable » maison, basés sur Tom Select (vanilla).

Remplacent les widgets ``django_select2`` (qui dépendaient de jQuery). Deux usages :

- petit jeu de données → ``TomSelectWidget`` / ``TomSelectMultipleWidget`` :
  toutes les ``<option>`` sont rendues côté serveur, Tom Select filtre côté client ;
- gros jeu (ex. artistes) → ``TomSelectRemoteWidget`` /
  ``TomSelectRemoteMultipleWidget`` : seules les options sélectionnées sont rendues,
  le reste est chargé à la frappe depuis un endpoint JSON (``search_url`` → ``?q=…``
  renvoyant ``[{"id": …, "text": …}, …]``).

L'initialisation JS est faite par ``assets/js/tomselect-init.js`` sur tous les
``<select class="js-tomselect">``. Les assets sont déclarés via ``Media`` et donc
chargés partout où le template rend ``{{ form.media }}``.
"""

from django import forms
from django.forms.models import ModelChoiceIterator


class TomSelectMixin:
    """Marque le ``<select>`` pour l'init Tom Select et porte les assets."""

    css_class = "js-tomselect"

    class Media:
        css = {"all": ("css/tom-select.css",)}
        js = ("js/tom-select.complete.min.js", "js/tomselect-init.js")

    def __init__(self, *args, **kwargs):
        self.placeholder = kwargs.pop("placeholder", None)
        super().__init__(*args, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        classes = attrs.get("class", "").split()
        if self.css_class not in classes:
            classes.append(self.css_class)
        attrs["class"] = " ".join(classes)
        placeholder = self.placeholder or attrs.pop("data-placeholder", None)
        if placeholder:
            attrs["data-placeholder"] = placeholder
        return attrs


class TomSelectWidget(TomSelectMixin, forms.Select):
    pass


class TomSelectMultipleWidget(TomSelectMixin, forms.SelectMultiple):
    pass


class TomSelectRemoteMixin(TomSelectMixin):
    """Charge les options à distance ; ne rend que les options sélectionnées."""

    def __init__(self, *args, search_url=None, **kwargs):
        self.search_url = search_url
        super().__init__(*args, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        if self.search_url:
            attrs["data-ts-url"] = str(self.search_url)
        return attrs

    def optgroups(self, name, value, attrs=None):
        # Ne rendre que les options sélectionnées : le reste vient de l'endpoint.
        selected = [v for v in (value or []) if v not in ("", None)]
        original = self.choices
        if not selected:
            self.choices = ()
        elif isinstance(original, ModelChoiceIterator):
            field = original.field
            objects = original.queryset.filter(pk__in=selected)
            self.choices = [
                (field.prepare_value(obj), field.label_from_instance(obj))
                for obj in objects
            ]
        else:
            wanted = {str(v) for v in selected}
            self.choices = [c for c in original if str(c[0]) in wanted]
        try:
            return super().optgroups(name, value, attrs)
        finally:
            self.choices = original


class TomSelectRemoteWidget(TomSelectRemoteMixin, forms.Select):
    pass


class TomSelectRemoteMultipleWidget(TomSelectRemoteMixin, forms.SelectMultiple):
    pass
