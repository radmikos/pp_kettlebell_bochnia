# tournament/apps.py

from django.apps import AppConfig


class TournamentAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tournament"

    def ready(self):
        # Importuj sygnały
        import tournament.signals
