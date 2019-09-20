from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="swagger-atlas",
    version="1.1.0",
    description="Transforms your swagger docs to load testing config and run them",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swagger-atlas/atlas",
    author="JTG",
    author_email="atlas@joshtechnologygroup.com",
    packages=find_packages(include=['atlas', 'atlas.*']),
    include_package_data=True,
    install_requires=[
        "six==1.11.0",
        "PyYAML==4.2b1",
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
