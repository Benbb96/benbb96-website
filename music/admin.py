from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
from django.contrib import admin
from django.db.models import Count
from simple_history.admin import SimpleHistoryAdmin

from music.models import Pays, Artiste, Style, Label, Playlist, Musique, MusiquePlaylist, Lien


@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


class MusiqueStyleInline(admin.TabularInline):
    model = Musique.styles.through
    autocomplete_fields = ('musique',)


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',), }
    save_on_top = True

    inlines = [MusiqueStyleInline]


class MusiquePlaylistInline(SortableTabularInline):
    model = MusiquePlaylist
    autocomplete_fields = ('musique',)
    readonly_fields = ('date_ajout',)


@admin.register(Playlist)
class PlaylistAdmin(NonSortableParentAdmin):
    list_display = ('nom', 'description', 'createur', 'nb_musique')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',), }
    save_on_top = True

    inlines = [MusiquePlaylistInline]

    def get_changeform_initial_data(self, request):
        return {'createur': request.user}

    def get_queryset(self, request):
        qs = super(PlaylistAdmin, self).get_queryset(request)
        return qs.annotate(nb_musique=Count('musiqueplaylist'))

    def nb_musique(self, obj):
        return obj.nb_musique
    nb_musique.short_description = 'Nombre de musique'
    nb_musique.admin_order_field = 'nb_musique'


class MusiqueInline(admin.StackedInline):
    model = Musique
    prepopulated_fields = {'slug': ('titre',), }
    autocomplete_fields = ('featuring', 'remixed_by', 'styles', 'createur')
    fk_name = 'artiste'
    extra = 0

    # TODO Remplir automatiquement le créateur pour la musique


class MusiqueRemixInline(admin.StackedInline):
    model = Musique
    prepopulated_fields = {'slug': ('titre',), }
    autocomplete_fields = ('featuring', 'remixed_by', 'styles',)
    fk_name = 'remixed_by'
    extra = 0
    verbose_name_plural = 'remixes'
    verbose_name = 'remix'

    # TODO Remplir automatiquement le créateur pour le remix


@admin.register(Artiste)
class ArtisteAdmin(SimpleHistoryAdmin):
    list_display = ('nom_artiste', 'nom', 'prenom', 'ville', 'pays', 'date_creation', 'date_modification')
    list_filter = ('styles', 'labels', 'createur')
    search_fields = (
        'nom_artiste', 'slug', 'prenom', 'nom',
    )
    date_hierarchy = 'date_creation'
    ordering = ('-date_modification',)
    prepopulated_fields = {'slug': ('nom_artiste',), }
    readonly_fields = ('soundcloud_followers', )
    autocomplete_fields = ('styles', 'pays', 'createur')
    save_on_top = True

    inlines = [MusiqueInline, MusiqueRemixInline]

    def get_changeform_initial_data(self, request):
        return {'createur': request.user}


class LienInline(admin.TabularInline):
    model = Lien


class PlaylistInline(admin.TabularInline):
    model = Playlist.musiques.through
    autocomplete_fields = ('playlist',)


@admin.register(Musique)
class MusiqueAdmin(SimpleHistoryAdmin):
    list_display = ('artiste_display', 'titre_display', 'album', 'label', 'createur',
                    'date_creation', 'date_modification', 'nb_vue')
    list_display_links = ('titre_display',)
    list_filter = ('styles', 'remixed_by')
    search_fields = (
        'titre', 'slug', 'artiste__nom_artiste', 'artiste__slug', 'remixed_by__nom_artiste', 'remixed_by__slug'
        'featuring__nom_artiste', 'featuring__slug', 'album', 'label__nom'
    )
    date_hierarchy = 'date_creation'
    ordering = ('-date_modification',)
    prepopulated_fields = {'slug': ('titre',), }
    autocomplete_fields = ('artiste', 'featuring', 'remixed_by', 'styles', 'label')
    list_select_related = ('artiste', 'remixed_by', 'createur__user', 'label')
    save_on_top = True
    list_per_page = 20

    inlines = [PlaylistInline, LienInline]

    def get_changeform_initial_data(self, request):
        return {'createur': request.user}


@admin.register(Lien)
class LienAdmin(admin.ModelAdmin):
    list_display = ('id', 'musique', 'url', 'plateforme', 'createur', 'click_count', 'date_creation', 'date_validation')
    list_filter = ('plateforme',)
    search_fields = (
        'musique__titre', 'musique__artiste__nom_artiste', 'plateforme'
    )
    date_hierarchy = 'date_creation'
    autocomplete_fields = ('musique',)
    list_select_related = ('musique__artiste', 'musique__remixed_by', 'createur__user')

    def get_changeform_initial_data(self, request):
        return {'createur': request.user}


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom', 'artistes__nom_artiste', 'styles__nom')
    prepopulated_fields = {'slug': ('nom',), }
    autocomplete_fields = ('artistes', 'styles')
