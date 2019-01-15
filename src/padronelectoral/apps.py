from django.apps import AppConfig


class PadronelectoralConfig(AppConfig):
    name = 'padronelectoral'

    def ready(self):

        import padronelectoral.signals