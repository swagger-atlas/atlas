from atlas.modules.resource_creator.creators import AutoGenerator


class TestAutoGenerator:

    def test_new_resource_are_created(self):
        instance = AutoGenerator()
        instance.parse()
        assert instance.new_resources == {"pet", "category"}
