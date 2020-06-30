import django_filters
from django import forms
from django.db.models import Q

from kendama.models import KendamaTrick, Combo


class BaseKendamaFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(
        label='Recherche',
        method='filter_text',
        widget=forms.TextInput(attrs={'class': 'input-block'})
    )
    difficulty = django_filters.ChoiceFilter(
        label='Difficulté',
        lookup_expr='exact',
        choices=KendamaTrick.DIFFICULTY,
        widget=forms.Select(attrs={'class': 'input-block'})
    )

    def filter_text(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(creator__user__username__icontains=value) |
            Q(creator__user__first_name__icontains=value) |
            Q(creator__user__last_name__icontains=value)
        )


class KendamaTrickFliter(BaseKendamaFilter):
    class Meta:
        model = KendamaTrick
        fields = ('text', 'difficulty')


class ComboFliter(BaseKendamaFilter):
    class Meta:
        model = Combo
        fields = ('text', 'difficulty')
