from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = "base"

    def ready(self):
        import base.signals  # noqa: F401  (import à effet de bord : branche les signaux)
