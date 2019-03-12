from atlas.modules.resource_data_generator.database import utils


class TestUtils:

    def test_flatten_list_of_tuples_no_data(self):
        assert utils.flatten_list_of_tuples([]) == ()

    def test_flatten_list_of_tuples_with_data(self):
        assert utils.flatten_list_of_tuples([(1,), (2, )]) == (1, 2)
