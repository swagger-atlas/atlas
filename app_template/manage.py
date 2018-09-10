import os

from atlas.modules.commands.management import CommandUtility


if __name__ == "__main__":

    # Set OS Variables for Settings
    module_path = "settings"
    class_name = "Settings"
    os.environ.setdefault("ATLAS_SETTINGS_MODULE", module_path)
    os.environ.setdefault("SETTINGS_CLASS", class_name)

    command = CommandUtility()
    command.execute()
