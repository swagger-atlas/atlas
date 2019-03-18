from setuptools import setup

setup(
    name="atlas",
    version="8.3.0",
    packages=["atlas"],
    install_requires=[
        "six==1.11.0",
        "PyYAML==3.13",
        "peewee==3.6.4",
        "pymysql==0.9.2",
        "psycopg2==2.7.5",
        "requests==2.20.0",
        "inflection==0.3.1",
        "pysed==0.7.8",
        "docker-compose>=1.23, <2.0"
    ],
    entry_points={
        'console_scripts': [
            'atlas = atlas.modules.commands.management:execute_from_command_line'
        ]
    }
)
