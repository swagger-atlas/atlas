import os
from unittest import mock

from atlas.modules.helpers.generate_routes import GenerateRoutes, settings


class TestGenerateRoutes:

    spec = {
        "paths": {
            "api": {
                "post": {
                    "operationId": "op_id"
                },
                "no_method": {},
                "get": {}
            },
            "no_method_api": {}
        }
    }

    def test_get_routes_valid_routes(self):
        gen_route = GenerateRoutes(self.spec)
        routes = ["API_CREATE = 'POST api'", "API_LIST = 'GET api'"]
        assert gen_route.get_routes() == "\n".join(routes)

    def test_get_routes_no_route(self):
        gen_route = GenerateRoutes({})
        assert gen_route.get_routes() == ""

    def test_write_to_routes(self):
        gen_route = GenerateRoutes({})
        gen_route.get_routes = mock.MagicMock(return_value="OP_ID = 'POST api'")

        gen_route.write_to_routes()

        with open(os.path.join(settings.INPUT_FOLDER, settings.ROUTES_FILE)) as _file:
            assert _file.read() == "OP_ID = 'POST api'\n"
