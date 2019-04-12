ATLAS Application
=================

This is an application build on ATLAS framework
Please see [ATLAS Documentation](https://github.com/swagger-atlas/atlas) for information about ATLAS.


Project Setup
=============

> If you have created project from `atlas newproject` command, skip to Step 4

1. Create a Virtual Environment, if not already created
    - Run `virtualenv <path/to/virtualenvs/atlas> -p <python3.x>`
     (Replace <variables> with your own versions). Python should be 3.6+
    - `source <path/to/virtualenvs/atlas>/bin/activate` to activate this

2. Run `pip install swagger-atlas`

3. Run `atlas build`

4. Customize as per your needs
    - Fill `settings.py` file
    - Update name in `package.json`

5. In the `conf` folder:
    - Copy your swagger to `swagger.yaml`
    - Fill in `conf.py` file
    - Copy `credentials.yaml.template` to `credentials.yaml`
    - Specify Resource mapping in `resource_mapping.yaml`
    - Write your resource hooks in `resource_hooks.py`
    - Task hooks as per task (For example, Artillery hooks are `artillery/hooks.js`)

    See: [Integration Use Cases](https://github.com/swagger-atlas/atlas/blob/master/docs/use_cases.md)


Setup InfluxDB and Grafana
==========================

We use InfluxDB to store all persistent raw reports.
Grafana is then used as visualization.


Docker Setup (Recommended)
--------------------------
You can easily setup both by running `docker-compose -f docker/docker-compose.yml up`


Manual Setup
------------

**InfluxDB**
- Install InfluxDB from: [InfluxDB Installation](https://docs.influxdata.com/influxdb/v1.7/introduction/installation/)
- Create a new database using: [Getting Started](https://docs.influxdata.com/influxdb/v1.7/introduction/getting-started/)
- Update your `settings.py` file for InfluxDB Settings

**Grafana**
- [Install Graphana](http://docs.grafana.org/installation/)
- Import `graphana.json` file in your Graphana dashboard. You may need to change DATA_SOURCE as per your settings


Running Artillery
=================

Build and Run Artillery:
    - `atlas dist`  (This converts your Swagger to Artillery Load Test)
    - `atlas run`   (This runs load test for your project)

You should see [Artillery Guide](https://github.com/swagger-atlas/atlas/blob/master/docs/artillery.md) for details.
