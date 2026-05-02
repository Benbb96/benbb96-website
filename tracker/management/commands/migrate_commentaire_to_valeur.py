from django.core.management.base import BaseCommand

from tracker.models import Tracker, Track


class Command(BaseCommand):
    help = 'Migre les valeurs numériques stockées dans commentaire vers le champ valeur'

    def add_arguments(self, parser):
        parser.add_argument('tracker_name', type=str, help='Nom exact du tracker à migrer')
        parser.add_argument('--dry-run', action='store_true', help='Prévisualise sans modifier la base')

    def handle(self, *args, **options):
        name = options['tracker_name']
        dry_run = options['dry_run']

        try:
            tracker = Tracker.objects.get(nom=name)
        except Tracker.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Tracker "{name}" introuvable.'))
            return

        tracks = tracker.tracks.all().order_by('datetime')
        migrated = skipped = errors = 0

        for track in tracks:
            commentaire = track.commentaire.strip()
            try:
                valeur = float(commentaire)
            except ValueError:
                self.stdout.write(self.style.WARNING(
                    f'  [{track.datetime:%d/%m/%y %H:%M}] commentaire non numérique ignoré : "{commentaire}"'
                ))
                errors += 1
                continue

            if dry_run:
                self.stdout.write(f'  [{track.datetime:%d/%m/%y %H:%M}] {commentaire!r} → valeur={valeur}')
            else:
                track.valeur = valeur
                track.commentaire = ''
                track.save(update_fields=['valeur', 'commentaire'])

            migrated += 1

        if not dry_run:
            tracker.type = Tracker.TYPE_MESURE
            tracker.save(update_fields=['type'])

        mode = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'\n{mode}Tracker "{name}" : {migrated} migré(s), {errors} ignoré(s), {skipped} déjà renseigné(s).'
        ))
