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
    - Task hooks as per task (For example, K6 hooks would be written in k6_hooks directory)
