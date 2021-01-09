from autoslug import AutoSlugField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from base.models import Profil


class Joueur(models.Model):
    nom = models.CharField(max_length=100)
    slug = AutoSlugField(unique=True, populate_from='nom')
    profil = models.OneToOneField(Profil, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('versus:detail-joueur', kwargs={'slug': self.slug})

    @cached_property
    def nb_victoire(self):
        nb = 0
        for partiejoueur in self.partiejoueur_set.all():
            if self in partiejoueur.partie.winners:
                nb += 1
        return nb

    @property
    def ratio(self):
        if self.partiejoueur_set.exists():
            return round(self.nb_victoire / self.partiejoueur_set.count() * 100)
        return None


class Jeu(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    createur = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)
    image = models.ImageField(
        help_text="Une image/photo pour identifier le jeu",
        null=True, blank=True, upload_to="jeux/"
    )
    SCORE = 1
    SCORE_INVERSE = 2
    CLASSEMENT = 3
    TYPES = (
        (SCORE, 'Score'),
        (SCORE_INVERSE, 'Score inverse'),
        (CLASSEMENT, 'Classement'),
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPES,
        default=SCORE,
        help_text="Sélectionner le type de jeu qui déterminera la façon de choisir le gagnant."
    )

    class Meta:
        verbose_name_plural = 'jeux'

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('versus:detail-jeu', kwargs={'slug': self.slug})

    def top_players(self):
        player_scores = {}
        for partie in self.parties.all():
            for joueur in partie.winners:
                if joueur not in player_scores.keys():
                    player_scores[joueur] = 1
                else:
                    player_scores[joueur] += 1
        # Tri des joueurspar nombre de parties gagnées
        player_scores = {k: v for k, v in sorted(player_scores.items(), key=lambda item: item[1], reverse=True)}

        top_players = []
        i = 1
        last_nb = None
        for joueur, nb in player_scores.items():
            # Incrémente la position si le nombre de victoire est plus bas
            if last_nb and last_nb > nb:
                i += 1
            top_players.append((i, joueur, nb))
            last_nb = nb

        return top_players


class Partie(models.Model):
    jeu = models.ForeignKey(Jeu, on_delete=models.CASCADE, related_name='parties')
    date = models.DateTimeField(default=timezone.now)
    joueurs = models.ManyToManyField(Joueur, through='PartieJoueur')

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return '%s (%s)' % (self.jeu, self.date)

    def classement_joueur(self):
        """ Retourne la liste des joueurs dans l'ordre de leur classement"""
        if self.jeu.type == Jeu.SCORE:
            return self.partiejoueur_set.order_by('-score_classement')
        return self.partiejoueur_set.order_by('score_classement')

    @cached_property
    def winners(self):
        """ Retourne le ou les gagnants de cette partie """
        if self.jeu.type == self.jeu.CLASSEMENT:
            # On veut la ou les personnes arrivées en première place
            return Joueur.objects.filter(partiejoueur__partie=self, partiejoueur__score_classement=1)
        else:
            if self.jeu.type == self.jeu.SCORE:
                # On cherche le score maximum
                valeur = max(partiejoueur.score_classement for partiejoueur in self.partiejoueur_set.all())
            else:
                # On cherche le score minimum
                valeur = min(partiejoueur.score_classement for partiejoueur in self.partiejoueur_set.all())
            # Puis on retourne tous les joueurs ayant ce score
            return Joueur.objects.filter(partiejoueur__partie=self, partiejoueur__score_classement=valeur)


class PartieJoueur(models.Model):
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE)
    score_classement = models.PositiveSmallIntegerField('score ou classement')

    class Meta:
        unique_together = (('partie', 'joueur'),)
