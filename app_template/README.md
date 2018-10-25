ATLAS Application
=======

This is an application build on ATLAS framework


Project Setup
======

1. Create a Virtual Environment
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


Running the Project
========

Please go through [ATLAS Docs](https://code.jtg.tools/jtg/atlas/README.md) for detailed run-down and options.

Build and Run Artillery:
    - `python manage.py dist k6`
    - `npm run-script artillery run dist/artillery.yaml

You would need to see [K6 Guide](https://code.jtg.tools/jtg/atlas/docs/k6.md) for details.
