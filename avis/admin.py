from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from avis.forms import AvisForm, ProduitForm
from .models import Profil, TypeStructure, Structure, Produit, Avis, CategorieProduit


class CategorieProduitInlineTypeStructure(admin.TabularInline):
    model = TypeStructure.categories.through


@admin.register(CategorieProduit)
class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',), }

    inlines = [CategorieProduitInlineTypeStructure]


class ProduitInLine(admin.StackedInline):
    model = Produit
    exclude = ('photo', )
    extra = 1
    show_change_link = True

    form = ProduitForm


@admin.register(TypeStructure)
class TypeStructureAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
    autocomplete_fields = ('categories',)


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'type', 'apercu_informations', 'position_map', 'nb_produit', 'moyenne', 'date_creation'
    )
    list_filter = ('type',)
    search_fields = ('nom', 'adresse')
    date_hierarchy = 'date_creation'
    ordering = ('nom', 'date_creation')
    prepopulated_fields = {'slug': ('nom',), }
    save_on_top = True

    inlines = [ProduitInLine]

    def moyenne(self, structure):
        return structure.moyenne
    moyenne.admin_order_field = 'moyenne'

    def nb_produit(self, structure):
        return structure.produit_count
    nb_produit.admin_order_field = 'produit_count'
    nb_produit.short_description = 'Nombre de produit'

    def position_map(self, instance):
        if instance.adresse is not None:
            # TODO Maybe need to add client ID and signature
            return format_html('<img src="http://maps.googleapis.com/maps/api/staticmap?key=%(map_api_key)s&center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'map_api_key': settings.GEOPOSITION_GOOGLE_MAPS_API_KEY[0],
                'latitude': instance.adresse.latitude,
                'longitude': instance.adresse.longitude,
                'zoom': 14,
                'width': 100,
                'height': 100,
                'scale': 2
            })
    position_map.short_description = 'Localisation'


class AvisInLine(admin.StackedInline):
    model = Avis
    fields = ('avis', 'note', 'photo', 'prive')
    extra = 1
    show_change_link = True
    ordering = ('date_creation',)

    form = AvisForm


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'structure', 'apercu_description', 'prix', 'moyenne', 'avis_count')
    list_filter = ('structure', )
    search_fields = ('nom', 'description', 'structure__nom')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    autocomplete_fields = ('structure', 'categories')
    list_select_related = ('structure__type',)
    save_on_top = True

    form = ProduitForm

    inlines = [AvisInLine]

    def save_formset(self, request, form, formset, change):
        if formset.model == Avis:
            avis_set = formset.save(commit=False)
            for avis in avis_set:
                avis.auteur = request.user.profil
                avis.save()
        else:
            formset.save()

    def moyenne(self, obj):
        return obj.moyenne
    moyenne.admin_order_field = 'moyenne'

    def avis_count(self, obj):
        return obj.avis_count
    avis_count.short_description = 'nb avis'
    avis_count.admin_order_field = 'avis_count'


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'structure', 'produit', 'auteur', 'apercu_avis', 'note',
        'date_creation', 'date_edition', 'prive', 'thumbnail'
    )
    list_filter = ('auteur', 'note', 'prive')
    search_fields = ('produit__nom', 'produit__structure__nom', 'auteur__user__username')
    date_hierarchy = 'date_creation'
    autocomplete_fields = ('produit',)
    readonly_fields = ('date_creation', 'date_edition')
    list_select_related = ('produit__structure',)
    save_on_top = True

    form = AvisForm

    def structure(self, avis):
        return avis.produit.structure

    structure.short_description = "Structure"

    def get_changeform_initial_data(self, request):
        """ Pré-rempli automatiquement avec l'utilisateur connecté """
        return {'auteur': request.user}

    def thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="50px" />', obj.get_photo_url())
        return 'Avis n°' + obj.id
