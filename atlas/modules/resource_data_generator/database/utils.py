def flatten_list_of_tuples(data):
    """
    Flatten List of tuples to single iterable
    [(1, ), (2, ), (3, )] --> (1, 2, 3)
    """
    return list(zip(*data))[0] if data else ()
