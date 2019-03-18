from unittest import mock

from atlas.modules.resource_creator.commands.generate import Generate


class TestGenerate:

    @mock.patch('atlas.modules.resource_creator.commands.generate.AutoGenerator')
    def test_handle(self, patch):
        instance = Generate()
        instance.handle()

        assert patch.mock_calls == [mock.call(), mock.call().parse(), mock.call().update()]
