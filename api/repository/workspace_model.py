from marshmallow import EXCLUDE, Schema, fields
from nxcore.repository.sqlite3_base_dao import SQLite3DAO

import config


class WorkspaceSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    _id = fields.Integer()
    name = fields.String()
    apikey = fields.String()
    instance_uid = fields.String()


class WorkspaceDao(SQLite3DAO):

    def __init__(self):
        super().__init__(
            db_path=config.DB_PATH,
            table_name="workspace",
            schema=WorkspaceSchema
        )

    def create_schema(self):
        """
        Creates the database table for workspace configuration if it doesn't already exist.
        """
        self.ddl(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                apikey TEXT,
                instance_uid TEXT
            );
        """)

    def get_first(self):
        """
        Retrieves the first workspace configuration record.

        Returns:
            dict: The workspace record if found, None otherwise.
        """
        sql = f"SELECT * FROM {self.table_name} LIMIT 1"
        rs = self._query(sql, fetch=True)
        row = rs[0] if rs else None
        return row
