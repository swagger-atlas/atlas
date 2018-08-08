import os
import importlib

ENVIRONMENT_VARIABLE = "ATLAS_SETTINGS_MODULE"


class Settings:

    def __init__(self, settings_module):

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        if not self.SETTINGS_MODULE:
            raise ValueError("Settings Module must be explicitly defined")

        mod = importlib.import_module(self.SETTINGS_MODULE)

        self.settings = mod.Settings


os.environ.setdefault(ENVIRONMENT_VARIABLE, 'settings.local')
settings = Settings(os.environ.get(ENVIRONMENT_VARIABLE)).settings
