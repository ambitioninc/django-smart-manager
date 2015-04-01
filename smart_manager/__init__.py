# flake8: noqa
from .version import __version__
from .base import BaseSmartManager
from .models import SmartManager, SmartManagerMixin, SmartModelMixin

django_app_config = 'smart_manager.apps.SmartManagerConfig'
