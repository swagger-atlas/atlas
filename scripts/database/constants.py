from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase


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
    POSTGRES: PostgresqlDatabase,
    SQLITE: SqliteDatabase,
    MySQLDatabase: MySQLDatabase
}
