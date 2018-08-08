import logging

from settings.conf import settings
from scripts.database import constants, utils

logger = logging.getLogger(__name__)


class Client:

    def __init__(self):
        self.db = self.connect_to_db()
        self.db.connect(reuse_if_open=True)

    def __del__(self):
        self.db.close()

    @staticmethod
    def connect_to_db():
        return constants.DATABASE_MAP.get(settings.DATABASE[constants.ENGINE])(
            settings.DATABASE[constants.NAME],
            user=settings.DATABASE[constants.USER],
            password=settings.DATABASE[constants.PASSWORD],
            host=settings.DATABASE[constants.HOST],
            port=settings.DATABASE[constants.PORT]
        )

    def execute_sql(self, sql):
        """
        Execute SQL Query
        :param sql: SQL Command
        :return: Result Cursor
        """
        logger.debug("Executing Query %s", sql)
        return self.db.execute_sql(sql)

    def fetch_rows(self, sql, mapper=None, include_headers=False):
        """
        :param sql: SQL Query
        :param mapper: Function to map results in specific way.
        :param include_headers: To include column names with result. Note this is ignored if row_mapper is provided
        :return: Iterable containing result
        """
        cursor = self.execute_sql(sql)
        result = cursor.fetchall()
        if mapper and callable(mapper):
            result = mapper(result)
        elif include_headers:
            result = (result, [desc[0] for desc in cursor.description])
        return result

    def fetch_ids(self, sql, mapper=None, include_headers=False):
        """
        :param sql: SQL Query
        :param mapper: Function to map results in specific way.
        :param include_headers: To include column names with result. Note this is ignored if row_mapper is provided
        :return: Tuple containing all values
        """

        if not mapper:
            # Flatten the list of tuples to single list
            mapper = utils.flatten_list_of_tuples

        return self.fetch_rows(sql, mapper, include_headers)
