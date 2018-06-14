from django.apps import AppConfig


class AvisConfig(AppConfig):
    name = 'avis'

    def ready(self):
        import avis.signals
