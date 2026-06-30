from typing import Dict, Any, Optional

from nxcore.middleware.logging_manager import logger
from nxcore.repository.sqlite3_dao import SQLite3DAO
from marshmallow import EXCLUDE, Schema, fields

import config as config


class OIDCToken(Schema):
    access_token = fields.String()
    refresh_token = fields.String()
    token_type = fields.String(load_default="Bearer", dump_default="Bearer")
    expires_in = fields.Integer()
    provider = fields.String()


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    _id = fields.Integer()
    name = fields.String()
    email = fields.String()
    password = fields.String()
    locale = fields.String(required=False)
    role = fields.String()
    service_token = fields.String(required=False, allow_none=True)


class UserDao(SQLite3DAO):

    def create_schema(self):
        self.ddl(
            f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        _id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        role TEXT,
                        service_token TEXT
                    );
                """
        )
        self.ddl(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON {self.table_name} (email);"
        )
        self.ddl(
            f"CREATE INDEX IF NOT EXISTS idx_users_role ON {self.table_name} (role);"
        )
        try:
            self.ddl(f"ALTER TABLE {self.table_name} ADD COLUMN service_token TEXT;")
        except Exception:
            pass

    def __init__(self):
        super().__init__(db_path=config.DB_PATH, table_name="users", schema=UserSchema)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            query = f"SELECT * from {self.table_name} WHERE email = ?"
            v = self._query(query, (email,), fetch=True)
            if v and v[0]:
                return super().to_dict(v[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by email: {str(e)}")
            raise
