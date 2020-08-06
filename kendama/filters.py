import django_filters
from django import forms
from django.db.models import Q

from kendama.models import KendamaTrick, Combo, Kendama, Ladder


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


class KendamaTrickFilter(BaseKendamaFilter):
    class Meta:
        model = KendamaTrick
        fields = ('text', 'difficulty')


class ComboFilter(BaseKendamaFilter):
    class Meta:
        model = Combo
        fields = ('text', 'difficulty')


class LadderFilter(BaseKendamaFilter):
    class Meta:
        model = Ladder
        fields = ('text', 'difficulty')

    @property
    def qs(self):
        """ Filtre les ladders pour ne faire apparaître que les publics
        ou bien ceux que l'utilisateur connecté a créé """
        parent = super().qs
        user = getattr(self.request, 'user', None)

        if user and not user.is_authenticated:
            return parent.public()

        return parent.filter(private=False) | parent.filter(creator__user=user)


class KendamaFliter(BaseKendamaFilter):
    text = django_filters.CharFilter(
        label='Recherche',
        method='filter_text',
        widget=forms.TextInput(attrs={'class': 'input-block'})
    )
    created_at__gte = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    created_at__lt = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lt',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Kendama
        fields = ('text', 'created_at__gte', 'created_at__lt')

    def filter_text(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(owner__user__username__icontains=value) |
            Q(owner__user__first_name__icontains=value) |
            Q(owner__user__last_name__icontains=value)
        )
