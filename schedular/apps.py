from django.apps import AppConfig
from schedular.main import Schedular
from django.conf import settings

class SchedularConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedular'

    def ready(self):
        if settings.SCHEDULAR:
            schedular = Schedular()
            schedular.run()

