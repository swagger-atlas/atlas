ATLAS
=======

- For those with mythological leanings, Atlas stand for the legend who carry the load of Earth on his shoulders
- For those who are dazzled with recursive structures, ATLAS is Tool for Load Analysis & Simulation
- For those who look still further (or backwards!), Simple Application for Load Testing and Analysis

ATLAS takes your Swagger, and smartly generates the code which could be used as input to various load testing tools.
Currently, ATLAS fully supports Artillery, and we have plans to incorporate for Locust Testing.


Quick Start
=====
- Install the Atlas Project by `pip install -e git@code.jtg.tools:jtg/atlas.git`
- Run `python atlas newproject <project-name>`
- Switch to new directory
- Update `settings.py`, `package.json`
- Run `npm install`
- Copy your swagger definition and Profiles in Conf directory


Artillery Load Test Basics
=======

Install Artillery:
    - `npm install -g artillery`
    - `npm install`

Build and Run Artillery:
    - `python manage.py dist artillery`
    - `artillery run dist/artillery.yaml

Please see [Artillery Guide](docs/artillery.md) for advanced usage of the same concept


Contributing to ATLAS
=========

Please see [Contribution Guide](docs/Contributing.md)
