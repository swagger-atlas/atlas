import os

from atlas.modules.commands.management import CommandUtility

if __name__ == "__main__":
    # Set OS Variables for Settings
    module_path = "settings"
    class_name = "Settings"

    conf_path = "conf.conf"
    conf_class_name = "Configuration"

    os.environ.setdefault("ATLAS_SETTINGS_MODULE", module_path)
    os.environ.setdefault("SETTINGS_CLASS", class_name)

    os.environ.setdefault("ATLAS_CONFIGURATION_MODULE", conf_path)
    os.environ.setdefault("CONFIGURATION_CLASS", conf_class_name)

    command = CommandUtility()
    command.execute()
