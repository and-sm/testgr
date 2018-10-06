from django.apps import AppConfig


class LoaderConfig(AppConfig):
    name = 'loader'

    def ready(self):
        import loader.signals