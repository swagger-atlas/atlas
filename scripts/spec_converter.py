from scripts import (
    locust_models,
    spec_models,
    utils,
)

specs = {
    "paths": {
        "/api/user/{id}": {
            "parameters": [
                {
                    "in": "path",
                    "name": "id",
                    "type": "integer",
                    "required": True
                }
            ],
            "get": {
                "summary": "This is sample API Summary",
                "operationID": "retrieveUser",
                "responses": {
                    "200": {
                        "description": "User Object",
                        "schema": {
                            "$ref": "#/definitions/user"
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "user": {
            "type": "object",
            "properties": {
                "id": {},
                "name": {}
            }
        }
    }
}


class LocustFileConfig:

    def __init__(self, task_set):
        self.task_set = task_set

        self.imports = ["from locust import HttpLocust, TaskSet, task"]
        self.global_vars = []

    def get_imports(self):
        return "\n".join(self.imports)

    def get_global_vars(self):
        return "\n".join(self.global_vars) if self.global_vars else ""

    def get_task_set(self):
        return self.task_set.convert()

    def convert(self):
        file_components = ["{imports}", "{declarations}", "{task_set}"]
        return "\n\n".join(file_components).format(**utils.StringDict(
            imports=self.get_imports(),
            declarations=self.get_global_vars(),
            task_set=self.task_set.convert(width=1)
        ))


if __name__ == "__main__":
    spec = spec_models.OpenAPISpec(specs)
    spec.get_tasks()
    tasks = locust_models.TaskSet(tasks=spec.tasks, tag="User")

    locust_file = LocustFileConfig(tasks)

    print(locust_file.convert())
