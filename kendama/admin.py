from django.contrib import admin

from base.admin import PhotoAdminAbtract
from kendama.forms import KendamaForm
from kendama.models import KendamaTrick, TrickPlayer, Combo, ComboPlayer, Kendama, ComboTrick


class BaseKendamaAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'difficulty', 'created_at')
    list_filter = ('difficulty',)
    search_fields = ('name', 'creator__username')
    date_hierarchy = 'created_at'
    prepopulated_fields = {'slug': ('name',), }
    autocomplete_fields = ('creator',)
    list_select_related = ('creator',)

    def get_changeform_initial_data(self, request):
        return {'creator': request.user.profil}


class TrickPlayerInline(admin.TabularInline):
    model = TrickPlayer


@admin.register(KendamaTrick)
class KendamaTrickAdmin(BaseKendamaAdmin):
    inlines = (TrickPlayerInline,)


class ComboTrickInline(admin.TabularInline):
    model = ComboTrick
    show_change_link = True


@admin.register(Combo)
class ComboAdmin(BaseKendamaAdmin):
    inlines = (ComboTrickInline,)


@admin.register(ComboTrick)
class ComboTrickAdmin(admin.ModelAdmin):
    list_display = ('combo', 'trick', 'order')
    list_select_related = ('combo', 'trick')


class BasePlayerFrequencyAdmin(admin.ModelAdmin):
    list_filter = ('frequency',)
    search_fields = ('trick__name', 'player__username')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('trick', 'player')

    def get_changeform_initial_data(self, request):
        return {'player': request.user.profil}


@admin.register(TrickPlayer)
class TrickPlayerAdmin(BasePlayerFrequencyAdmin):
    list_display = ('id', 'trick', 'player', 'frequency', 'created_at')
    autocomplete_fields = ('trick', 'player')
    list_select_related = ('trick', 'player')


@admin.register(ComboPlayer)
class ComboPlayerAdmin(BasePlayerFrequencyAdmin):
    list_display = ('id', 'combo', 'player', 'frequency', 'created_at')
    autocomplete_fields = ('combo', 'player')
    list_select_related = ('combo', 'player')


@admin.register(Kendama)
class KendamaAdmin(PhotoAdminAbtract):
    list_display = ('thumbnail', 'name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
    prepopulated_fields = {'slug': ('name',), }
    list_select_related = ('owner',)

    form = KendamaForm

    def get_changeform_initial_data(self, request):
        return {'owner': request.user.profil}

