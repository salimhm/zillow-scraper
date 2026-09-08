"""Django application configuration for the scraper app."""

from django.apps import AppConfig


class ScrapersConfig(AppConfig):
    name = 'scrapers'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Keep startup side-effect free; sessions are created on demand."""
        return None
