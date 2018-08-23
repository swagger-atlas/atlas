ATLAS
=======

- For those with mythological leanings, Atlas stand for the legend who carry the load of Earth on his shoulders
- For those who are dazzled with recursive structures, ATLAS is Tool for Load Analysis & Simulation
- For those who look still further (or backwards!), Simple Application for Load Testing and Analysis


Project Setup
======

1. Create a Virtual Environment
    - Run `virtualenv <path/to/virtualenvs/atlas> -p <python3.x>`
     (Replace <variables> with your own versions). Python should be 3.5+
    - `source <path/to/virtualenvs/atlas>/bin/activate` to activate this

2. Run requirements
    - `pip install -r requirements.txt`
    - See `http://initd.org/psycopg/docs/install.html#build-prerequisites` in case there are issues with Postgres Client

3. Set up Pylint Hook
    - Create a file under .git/hooks/ with name pre-commit
    - Add to that file:
       ```bash
        #!/usr/bin/env bash
        /path/to/git-pylint-commit-hook --pylint /path/to/pylint --pylintrc pylint.rc
       ```
    - Update the permissions by `chmod +x .git/hooks/pre-commit`

    You can run pylint anytime by using `pylint --rcfile=pylint.rc <file_path>`

4. Customize as per your needs
    - Create a sub-folder under "project"
    - In your newly created sub-folder:
        - Create a folder called "resources"
        - Copy your swagger definition
        - Copy hooks.py.template and rename it as hooks.py
        - Add any mapping hooks as map_hooks.py
        - Create the profiles as "profiles.yaml"
        - Add your mapping file as res_mapping.yaml ([YAML](docs/yaml.md))
    - Copy local.py.template to local.py in Settings folder and fill in the appropriate settings


How to Use
===========

Auto-generating Resources from Swagger
------
1. Run `scripts/resources/auto_generate.py`.
    - Updated resources will be available in MAPPING_FILE.
    - Your SWAGGER_FILE would also have been updated

Converting Specs to Locust
------
1. You can convert OpenAPI Specifications using `scripts/spec_converter.py`

Creating a Resource Pool from Resource Mapping
-----
You can try and create a temporary resource map for testing
1. Use `parse` method of ``ResourceMap` class defined in `resources/generators`.


Running Locust
------
1. You can run locust from executing `scripts/locust_runner.py` file


Contributing to ATLAS
=========

Please see [Contribution Guide](docs/Contributing.md)
