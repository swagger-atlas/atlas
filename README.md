ATLAS
=======

- For those with mythological leanings, Atlas stand for the legend who carry the load of Earth on his shoulders
- For those who are dazzled with recursive structures, ATLAS is Tool for Load Analysis & Simulation
- For those who look still further (or backwards!), Simple Application for Load Testing and Analysis

ATLAS takes your Swagger, and smartly generates the code which could be used as input to various load testing tools.
Currently, ATLAS fully supports K6, and we have plans to incorporate for Locust Testing.


Quick Start
=====
- Install the Atlas Project by `pip install -e git@code.jtg.tools:jtg/atlas.git`
- Run `python atlas newproject <project-name>`
- Switch to new directory
- Copy your swagger definition and Profiles in Conf directory
- Run `python manage.py generate`


K6 Load Test Basics
=======

- One Time setup: `python manage.py setup k6`
- Install k6 (https://docs.k6.io/docs/installation)
- And then:
    - `python manage.py build k6`
    - `python manage.py dist k6`
    - `k6 run dist/k6.js -u <number_of_users> -i <number_of_iterations>` [See: https://docs.k6.io/docs/options]

Please see [K6 Guide](docs/k6.md) for advanced usage of the same concept


Contributing to ATLAS
=========

Please see [Contribution Guide](docs/Contributing.md)
