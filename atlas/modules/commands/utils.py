def add_bool_arg(parser, name, default=False, **options):
    """
    Python Command line does not play well with Boolean arguments

    So we add this nice little snippet.

    Usage:
        add_bool_arg(parser, 'my-feature')
    """

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=name, action='store_true', **options)
    group.add_argument('--no-' + name, dest=name, action='store_false', **options)
    parser.set_defaults(**{name:default})
