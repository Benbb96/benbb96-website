from django.contrib import admin
from django.utils.html import format_html

from base.admin import PhotoAdminAbtract
from super_moite_moite.forms import TacheForm
from super_moite_moite.models import Logement, Categorie, Tache, PointTache, TrackTache


class CategorieInlineAdmin(admin.TabularInline):
    model = Categorie
    show_change_link = True


@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'date_creation')
    search_fields = ('nom', 'habitants__user__username')
    date_hierarchy = 'date_creation'
    prepopulated_fields = {'slug': ('nom',), }

    inlines = (CategorieInlineAdmin,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(habitants=request.user.profil)
        return queryset


class TacheInlineAdmin(admin.StackedInline):
    model = Tache
    form = TacheForm
    show_change_link = True


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'logement', 'order', 'affiche_couleur')
    search_fields = ('nom', 'logement__nom')
    list_select_related = ('logement',)

    inlines = (TacheInlineAdmin,)

    def affiche_couleur(self, instance):
        return format_html(
            '<div style="padding: 5px; background-color: {color}">{color}</div>',
            color=instance.couleur
        )
    affiche_couleur.admin_order_field = 'couleur'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(logement__habitants=request.user.profil)
        return queryset


class PointTacheInlineAdmin(admin.TabularInline):
    model = PointTache
    autocomplete_fields = ('profil',)


@admin.register(Tache)
class TacheAdmin(PhotoAdminAbtract):
    list_display = ('thumbnail', 'nom', 'categorie', 'order')
    search_fields = ('nom', 'categorie__nom', 'categorie__logement__nom')
    fields = ('nom', 'categorie', 'description', 'photo')
    list_select_related = ('categorie',)

    form = TacheForm

    inlines = (PointTacheInlineAdmin,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(categorie__logement__habitants=request.user.profil)
        return queryset


@admin.register(PointTache)
class PointTacheAdmin(admin.ModelAdmin):
    list_display = ('profil', 'tache', 'point')
    list_filter = ('point',)
    list_select_related = ('profil', 'tache')
    autocomplete_fields = ('profil', 'tache')
    search_fields = ('tache__nom', 'tache__categorie__nom', 'tache__categorie__logement__nom', 'profil__user__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(tache__categorie__logement__habitants=request.user.profil)
        return queryset


@admin.register(TrackTache)
class TrackTacheAdmin(admin.ModelAdmin):
    list_display = ('id', 'tache', 'profil', 'datetime', 'commentaire')
    list_filter = ('datetime',)
    list_select_related = ('profil', 'tache')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)
    search_fields = (
        'tache__nom', 'tache__categorie__nom', 'tache__categorie__logement__nom', 'commentaire',
        'profil__user__username'
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(tache__categorie__logement__habitants_=request.user.profil)
        return queryset

    def get_changeform_initial_data(self, request):
        return {'profil': request.user.profil}
