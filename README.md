ATLAS
=======

- For those with mythological leanings, Atlas stand for the legend who carry the load of Earth on his shoulders
- For those who are dazzled with recursive structures, ATLAS is Tool for Load Analysis & Simulation
- For those who look still further (or backwards!), Simple Application for Load Testing and Analysis

ATLAS takes your Swagger, and smartly generates the code which could be used as input to various load testing tools.
Currently, ATLAS fully supports Artillery, and we have plans to incorporate for Locust Testing.


Creating a new Project
=====
- Create a virtual environment
- Install the Atlas Project by `pip install -e git@code.jtg.tools:jtg/atlas.git`
- Run `python atlas newproject <project-name>`
- Switch to new directory
- Follow the README of directory to customize and run your load test

Note: Atlas generates code in Python 3.5+ and JS.
Your servers could be in any language :)


Contributing to ATLAS
=========

Please see [Contribution Guide](docs/Contributing.md)
