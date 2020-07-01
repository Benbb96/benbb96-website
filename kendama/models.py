from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from base.models import Profil, PhotoAbstract


class BaseKendamaModel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        Profil,
        on_delete=models.SET_NULL,
        verbose_name='créateur',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField('date création', auto_now_add=True)
    updated_at = models.DateTimeField('date mise à jour', auto_now=True)
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    DIFFICULTY = (
        (BEGINNER, 'Débutant'),
        (INTERMEDIATE, 'Intermédiaire'),
        (ADVANCED, 'Avancé'),
    )
    difficulty = models.PositiveSmallIntegerField(
        'difficulté',
        choices=DIFFICULTY
    )
    tutorial_video_link = models.URLField('lien vidéo tutoriel', blank=True)
    # TODO proof_video

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class KendamaTrick(BaseKendamaModel):
    # TODO photo
    players = models.ManyToManyField(
        Profil,
        verbose_name='joueurs',
        related_name='tricks',
        through='TrickPlayer',
        blank=True
    )

    class Meta:
        verbose_name = 'trick de Kendama'
        verbose_name_plural = 'tricks de Kendama'
        ordering = ('-created_at',)

    def get_absolute_url(self):
        return reverse('kendama:detail-trick', args=[self.slug])


class BasePlayerFrequency(models.Model):
    player = models.ForeignKey(
        Profil,
        on_delete=models.CASCADE,
        verbose_name='joueur'
    )
    IMPOSSIBLE = 1
    ONCE = 2
    RARELY = 3
    SOMETIMES = 4
    GENERALLY = 5
    ALWAYS = 6
    FREQUENCY = (
        (IMPOSSIBLE, 'Impossible'),
        (ONCE, 'Seulement une fois'),
        (RARELY, 'Rarement'),
        (SOMETIMES, 'Parfois'),
        (GENERALLY, 'Généralement'),
        (ALWAYS, 'Tout le temps'),
    )
    frequency = models.PositiveSmallIntegerField(
        'fréquence de réussite',
        choices=FREQUENCY,
        default=IMPOSSIBLE
    )
    created_at = models.DateTimeField('date création', auto_now_add=True)

    # TODO proof_video

    class Meta:
        abstract = True


class TrickPlayer(BasePlayerFrequency):
    trick = models.ForeignKey(KendamaTrick, on_delete=models.PROTECT, related_name='trick_players')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'trick de joueur'
        verbose_name_plural = 'tricks de joueur'
        unique_together = ('trick', 'player')

    def __str__(self):
        return f'{self.player} - {self.trick} : {self.get_frequency_display()}'


class Combo(BaseKendamaModel):
    tricks = models.ManyToManyField(KendamaTrick, related_name='combos', through='ComboTrick')
    players = models.ManyToManyField(
        Profil,
        verbose_name='joueurs',
        related_name='combos',
        through='ComboPlayer',
        blank=True
    )

    class Meta:
        ordering = ('-created_at',)

    def get_absolute_url(self):
        return reverse('kendama:detail-combo', args=[self.slug])


class ComboTrick(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='combo_tricks')
    trick = models.ForeignKey(KendamaTrick, on_delete=models.PROTECT, related_name='combo_tricks')
    order = models.PositiveSmallIntegerField('ordre', default=0, db_index=True)


class ComboPlayer(BasePlayerFrequency):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='combo_players')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'combo de joueur'
        verbose_name_plural = 'combos de joueur'
        unique_together = ('combo', 'player')

    def __str__(self):
        return f'{self.player} - {self.combo} : {self.get_frequency_display()}'


class Kendama(PhotoAbstract):
    owner = models.ForeignKey(
        Profil,
        on_delete=models.CASCADE,
        verbose_name='possesseur',
        related_name='kendamas'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    created_at = models.DateTimeField('date de création', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name
