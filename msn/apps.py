from django.apps import AppConfig


class MsnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msn'

    def ready(self):
        import msn.signals  # noqa
