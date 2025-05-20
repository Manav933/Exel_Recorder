from django.apps import AppConfig

class InvoiceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Recorder'
    verbose_name = 'Invoice Manager'
    
    def ready(self):
        """
        Import signals when the app is ready
        """
        import Recorder.signals  # noqa