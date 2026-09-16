"""Génération de slugs : translittération via python-slugify et unicité par modèle."""

from slugify import slugify


def unique_slugify(instance, value, slug_field="slug"):
    """Slug translittéré, tronqué à la taille du champ, suffixé -2, -3… si le champ est unique."""
    field = instance._meta.get_field(slug_field)
    max_length = field.max_length or 0
    # Repli sur le nom du modèle quand la translittération ne laisse rien (emojis, ponctuation seule)
    base = slugify(value, max_length=max_length) or instance._meta.model_name

    if not field.unique:
        return base

    queryset = instance.__class__._base_manager.all()
    if instance.pk is not None:
        queryset = queryset.exclude(pk=instance.pk)

    slug, counter = base, 1
    while queryset.filter(**{slug_field: slug}).exists():
        counter += 1
        suffixe = f"-{counter}"
        tronque = base[: max_length - len(suffixe)].rstrip("-") if max_length else base
        slug = f"{tronque}{suffixe}"
    return slug
