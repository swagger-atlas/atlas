from setuptools import setup

setup(
    name="atlas",
    version="0.14",
    packages=["atlas"],
    install_requires=[
        "six==1.11.0",
        "PyYAML==3.13",
        "peewee==3.6.4",
        "pymysql==0.9.2",
        "psycopg2==2.7.5",
        "requests==2.19.1",
        "inflection==0.3.1",
        "pysed==0.7.8"
    ]
)
