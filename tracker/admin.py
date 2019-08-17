from adminsortable.admin import SortableAdmin
from django.contrib import admin

from base.models import Profil
from tracker.models import Tracker, Track


class TrackInline(admin.TabularInline):
    model = Track


@admin.register(Tracker)
class TrackerAdmin(SortableAdmin):
    list_display = ('nom', 'createur', 'icone', 'color', 'date_creation')
    search_fields = ('createur__user__username', 'nom')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)

    inlines = [TrackInline]

    def get_form(self, request, obj=None, **kwargs):
        # Pré-rempli automatiquement avec l'utilisateur connecté
        form = super(TrackerAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['createur'].initial = Profil.objects.get(user=request.user)
        return form


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'tracker', 'datetime', 'commentaire')
    date_hierarchy = 'datetime'
    ordering = ('-datetime',)
    search_fields = ('tracker__nom', 'commentaire')
