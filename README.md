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
    - Copy local.py.template to local.py in Settings folder and fill in the appropriate settings


How to Use
===========

Setup your Project Files
-------
1. Run `scripts/project_setup.py`
1. In newly set up folder, navigate to input folder. There:
    - Copy your swagger definition
    - Copy hooks.py.template
    - Add any mapping hooks as map_hooks.py
    - Create the profiles as "profiles.yaml"
    - Add your mapping file as res_mapping.yaml ([YAML](docs/yaml.md))
1. Names for above should match as specified in settings file

Auto-generating Resources from Swagger
------
1. Run `scripts/resources/auto_generate.py`.
    - Updated resources will be available in MAPPING_FILE.
    - SWAGGER_FILE would also be generated again in Output path

Creating a Resource Pool from Resource Mapping
-----
1. Run the auto-generation of resources outlined above
1. Use `parse` method of ``ResourceMap` class defined in `resources/generators`.

Converting Specs to Locust
------
1. Create the Resource Pool as outlined above
1. You can convert OpenAPI Specifications using `scripts/spec_converter.py`

Running Locust
------
1. You can run locust from executing `scripts/locust_runner.py` file


Contributing to ATLAS
=========

Please see [Contribution Guide](docs/Contributing.md)
