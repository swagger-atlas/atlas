import os
from os import path
from unittest import mock

from atlas.modules.transformer.artillery.dist import ArtilleryDist, settings


class TestDist:

    def test_start(self):
        instance = ArtilleryDist()
        instance.create_folder = mock.MagicMock()
        instance.copy_files = mock.MagicMock()
        instance.copy_folders = mock.MagicMock()

        instance.start()

        assert instance.create_folder.mock_calls == [
            mock.call(settings.DIST_FOLDER),
            mock.call(settings.ARTILLERY_FOLDER, os.path.join(instance.path, settings.DIST_FOLDER))
        ]

        instance.copy_files.assert_called_once()
        instance.copy_folders.assert_called_once()

    @mock.patch('atlas.modules.transformer.artillery.dist.shutil')
    @mock.patch('atlas.modules.transformer.artillery.dist.os.path.isfile')
    def test_copy_files_all_files(self, patch_os_is_file, patched_shell):

        patch_os_is_file.return_value = True

        instance = ArtilleryDist()
        instance.path = ""

        instance.copy_files()

        source_path = path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "artillery")
        source_files = [path.join(source_path, file) for file in os.listdir(source_path)
                        if file not in {"constants.js", "settings.js", settings.ARTILLERY_RESOURCES}]
        d_path = path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_LIB_FOLDER)

        expected_sources = [((_file, d_path),) for _file in source_files]

        expected_sources.extend([
            (
                (
                    path.join(settings.INPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_HOOK_FILE),
                    path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER)
                ),
            ),
            (
                (
                    path.join(settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_FILE),
                    path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER)
                ),
            ),
            (
                (
                    path.join(settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_YAML),
                    path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER)
                ),
            ),
            (
                (
                    path.join(settings.OUTPUT_FOLDER, settings.SWAGGER_FILE),
                    path.join(settings.DIST_FOLDER)
                ),
            )
        ])

        assert patched_shell.copy.call_args_list == expected_sources

    @mock.patch('atlas.modules.transformer.artillery.dist.shutil')
    @mock.patch('atlas.modules.transformer.artillery.dist.os.path.isfile')
    def test_copy_files_no_files(self, patch_os_is_file, patched_shell):
        patch_os_is_file.return_value = False

        instance = ArtilleryDist()
        instance.path = ""

        instance.copy_files()

        expected_sources = [
            (
                (
                    path.join(settings.INPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_HOOK_FILE),
                    path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER)
                ),
            ),
            (
                (
                    path.join(settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_FILE),
                    path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER)
                ),
            ),
            (
                (
                    path.join(settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_YAML),
                    path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER)
                ),
            ),
            (
                (
                    path.join(settings.OUTPUT_FOLDER, settings.SWAGGER_FILE),
                    path.join(settings.DIST_FOLDER)
                ),
            )
        ]

        assert patched_shell.copy.call_args_list == expected_sources

    @mock.patch('atlas.modules.transformer.artillery.dist.shutil')
    @mock.patch('atlas.modules.transformer.artillery.dist.os.path.exists')
    def test_copy_folders_destination_exists(self, patch_os_path_exists, patched_shell):

        patch_os_path_exists.return_value = True

        instance = ArtilleryDist()
        instance.path = ""

        instance.copy_folders()

        patched_shell.rmtree.assert_called()
        patched_shell.copytree.assert_called()

    @mock.patch('atlas.modules.transformer.artillery.dist.shutil')
    @mock.patch('atlas.modules.transformer.artillery.dist.os.path.exists')
    def test_copy_folders_destination_not_exists(self, patch_os_path_exists, patched_shell):
        patch_os_path_exists.return_value = False

        instance = ArtilleryDist()
        instance.path = ""

        instance.copy_folders()

        patched_shell.rmtree.assert_not_called()
        patched_shell.copytree.assert_called()

    @mock.patch('atlas.modules.transformer.artillery.dist.os.makedirs')
    @mock.patch('atlas.modules.transformer.artillery.dist.os.path.exists')
    def test_create_folder_path_exists(self, patch_os_path_exists, patched_makedir):
        patch_os_path_exists.return_value = True

        instance = ArtilleryDist()
        instance.path = ""

        instance.create_folder('folder')

        patched_makedir.assert_not_called()

    @mock.patch('atlas.modules.transformer.artillery.dist.os.makedirs')
    @mock.patch('atlas.modules.transformer.artillery.dist.os.path.exists')
    def test_create_folder_path_not_exists(self, patch_os_path_exists, patched_makedir):
        patch_os_path_exists.return_value = False

        instance = ArtilleryDist()
        instance.path = ""

        instance.create_folder('folder')

        patched_makedir.assert_called()
