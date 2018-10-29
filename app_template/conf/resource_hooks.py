"""
Resource Hooks

Resource Hooks are created when you want to manually add the data in cache instead of Database

Resource_mapping File
-----------
This is how resource_mapping.yaml file would look like:

resource_name:
    source: script
    func: my_func_name
    args:
        - 1
        - 2
    kwargs:
        a: 1

Here, args and kwargs are optional.


Resource Hooks File
-----------
In this file, a corresponding function would look like:

def my_func_name(arg_1, arg_2, a):
    return [arg_1 + arg_2 + a, arg_1, arg_2]

Note: Function MUST return a list, even if it single value.
"""
