"""
Resource Hooks

This file contains two kinds of functions:

1. Resource Hooks
    These are created when you want to manually add the data in cache instead of Database
2. Mapper Functions
    These are post-process function for DB Table Resources

Resource Hooks
======

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


Mapper Functions
========

Resource_mapping File
-----------
This is how resource_mapping.yaml file would look like:

resource_name:
    table: table_xyz
    mapper: my_mapper


Resource Hooks File
-----------
In this file, a corresponding function would look like:

def my_mapper(data):
    return [x+1 for x in zip(*data)[0]] if data else []

Note:
    Function MUST return a list, and accepts a single argument which contains result of DB Query.
    DB Query Result is usually a list of tuples

"""


def get_category():
    return [1]


def get_tag():
    return [1]


def get_pet():
    return [1]
