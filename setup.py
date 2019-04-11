from setuptools import setup

setup(
    name="swagger-atlas",
    version="1.0.0",
    description="Transforms your swagger docs to load testing config and run them",
    url="https://github.com/swagger-atlas/atlas",
    author_email="atlas@joshtechnologygroup.com",
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
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
    ],
)
