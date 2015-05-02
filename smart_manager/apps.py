from django.apps import AppConfig


class SmartManagerConfig(AppConfig):
    name = 'smart_manager'
    verbose_name = 'Django Smart Manager'

    def ready(self):
        import smart_manager.signal_handlers
        assert(smart_manager)
