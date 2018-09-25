from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase

from atlas.conf import settings


# Settings constants
ENGINE = "engine"
NAME = "name"
HOST = "host"
PASSWORD = "password"
PORT = "port"
USER = "user"


# Engine Constants
POSTGRES = "postgres"
SQLITE = "sqlite"
MYSQL = "mysql"


# Engine mappings
DATABASE_MAP = {
    POSTGRES: {
        "engine": PostgresqlDatabase,
        "args": {
            "user": settings.DATABASE[USER],
            "password": settings.DATABASE[PASSWORD],
            "host": settings.DATABASE[HOST],
            "port": settings.DATABASE[PORT]
        }
    },
    SQLITE: {
        "engine": SqliteDatabase,
        "args": {}
    },
    MySQLDatabase: {
        "engine": MySQLDatabase,
        "args": {
            "user": settings.DATABASE[USER],
            "password": settings.DATABASE[PASSWORD],
            "host": settings.DATABASE[HOST],
            "port": settings.DATABASE[PORT]
        }
    }
}
