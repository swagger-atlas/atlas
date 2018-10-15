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

1. In the conf folder:
    - Copy your swagger to swagger.yaml
    - Write your resource hooks in resource_hooks.py
    - Resource mapping in resource_mapping.yaml
    - Task hooks as per task (For example, K6 hooks are hooks.js)


Running the Project
========

Please go through [ATLAS Docs](https://code.jtg.tools/jtg/atlas/README.md) for detailed run-down and options.

Quick K6 Run:

- Install and Run Redis Server: https://redis.io/download
- Install and run Webdis server: https://github.com/nicolasff/webdis

- Install k6 (https://docs.k6.io/docs/installation)

Build and Run K6:
    - `python manage.py dist k6`
    - `k6 run dist/k6.js -u <number_of_users> -i <number_of_iterations>` [See: https://docs.k6.io/docs/options]

If your swagger updates:
    - `python manage.py dist k6 --no-setup`
    - `k6 run dist/k6.js -u <number_of_users> -i <number_of_iterations>` [See: https://docs.k6.io/docs/options]

You would need to see [K6 Guide](https://code.jtg.tools/jtg/atlas/docs/k6.md) for details.
