import os
import importlib

from atlas.settings import Settings as baseSettings


SETTINGS_MODULE = "ATLAS_SETTINGS_MODULE"
SETTINGS_CLASS = "SETTINGS_CLASS"

CONF_MODULE = "ATLAS_CONFIGURATION_MODULE"
CONF_CLASS = "CONFIGURATION_CLASS"

empty = object()


def new_method_proxy(func):
    def inner(self, *args):
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazySettings:
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class.

    This is taken from django LazyObject and LazySettings
    however, we simplified it greatly so that it just meet our needs
    """

    _wrapped = None

    def __init__(self):
        self._wrapped = empty

    def _setup(self):
        settings_module = os.environ.get(SETTINGS_MODULE)
        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        """
        Return the value of a setting and cache it in self.__dict__.
        """
        if self._wrapped is empty:
            self._setup()
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        """
        Set the value of setting. Clear all cached values if _wrapped changes
        or clear single values when set.
        """
        if name == '_wrapped':
            self.__dict__.clear()
            self.__dict__["_wrapped"] = value
        else:
            self.__dict__.pop(name, None)
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    # Introspection support
    __dir__ = new_method_proxy(dir)


class Settings:

    def set_settings(self, setting_class):
        for setting in dir(setting_class):
            # Ignore the dunder variables, since there are high chances it is python built-in
            if setting.startswith("__"):
                continue
            setattr(self, setting, getattr(setting_class, setting))

    def __init__(self, settings_module):

        # First get the settings as defined by ATLAS
        self.set_settings(baseSettings)

        # Now try to get settings as defined by user
        # Any user defined settings take higher priority than our base settings
        if settings_module:
            mod = importlib.import_module(settings_module)
            user_settings = getattr(mod, os.environ.get(SETTINGS_CLASS, "Settings"))
            self.set_settings(user_settings)

        # Add configuration settings
        conf_module = os.environ.get(CONF_MODULE)
        if conf_module:
            mod = importlib.import_module(conf_module)
            user_settings = getattr(mod, os.environ.get(CONF_CLASS, "Configuration"))
            self.set_settings(user_settings)


settings = LazySettings()
