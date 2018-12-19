ATLAS Application
=======

This is an application build on ATLAS framework
Please see [ATLAS Documentation](https://code.jtg.tools/jtg/atlas/README.md) for information about ATLAS.

Project Setup
======

1. Create a Virtual Environment, if not already created
    - Run `virtualenv <path/to/virtualenvs/atlas> -p <python3.x>`
     (Replace <variables> with your own versions). Python should be 3.5+
    - `source <path/to/virtualenvs/atlas>/bin/activate` to activate this

1. Customize as per your needs
    - Fill settings.py file
    - Update name in package.json
    - Run `npm install`

1. In the conf folder:
    - Copy your swagger to swagger.yaml
    - Write your resource hooks in resource_hooks.py
    - Resource mapping in resource_mapping.yaml
    - Task hooks as per task (For example, Artillery hooks are hooks.js)

    See: [Integration Use Cases](https://code.jtg.tools/jtg/atlas/docs/use_cases.md)


Running Artillery
========

Install Artillery and dependencies:
    - `npm install -g artillery`
    - `npm install`

Build and Run Artillery:
    - `python manage.py dist artillery`
    - `artillery run dist/artillery/artillery.yaml`

You should see [Artillery Guide](https://code.jtg.tools/jtg/atlas/docs/artillery.md) for details.
