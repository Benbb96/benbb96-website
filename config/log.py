"""Handlers de logging du projet."""

from django.utils.log import AdminEmailHandler


class SafeAdminEmailHandler(AdminEmailHandler):
    """`AdminEmailHandler` dont l'échec d'envoi ne peut pas remonter.

    Depuis le passage aux MAILERS, Django a perdu le `fail_silently=True` qu'il
    appliquait à cet envoi : un ESP en panne fait alors lever le handler de
    logging lui-même, hors de la pile Django (plus de page 500, erreur d'origine
    masquée). `handleError()` renvoie la trace sur stderr au lieu de propager.
    """

    def emit(self, record):
        try:
            super().emit(record)
        except Exception:
            self.handleError(record)
