from datetime import datetime

from basic4web.repository.sqlite3_base_dao import SQLite3DAO

import config


class FeedDao(SQLite3DAO):

    def __init__(self):
        super().__init__(db_path=config.DB_PATH, table_name="feed")

    def create_schema(self):
        """
        Creates the database table for feeds if it doesn't already exist.
        """
        self.ddl(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                slug TEXT,
                provider TEXT,
                restricted TEXT,
                type TEXT,
                action TEXT,
                source TEXT,
                description TEXT,
                format TEXT,
                update_interval TEXT,
                updated_on TEXT,
                risk_score INTEGER
            );
        """)

    def from_dict(self, vo):
        """
        Converts a dictionary to a format suitable for database insertion,
        specifically handling datetime conversion for 'updated_on'.

        Args:
            vo (dict): The dictionary to convert.

        Returns:
            dict: The converted dictionary.
        """
        if "updated_on" in vo:
            vo.update({"updated_on": vo["updated_on"].isoformat()})
        return super().from_dict(vo)

    def to_dict(self, row):
        """
        Converts a database row back to a dictionary, specifically handling
        datetime conversion for 'updated_on'.

        Args:
            row (dict): The database row to convert.

        Returns:
            dict: The converted dictionary.
        """
        if "updated_on" in row and row["updated_on"] is not None:
            row.update({"updated_on": datetime.fromisoformat(row["updated_on"])})
        return row
