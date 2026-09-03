from datetime import datetime, timezone
import json
from nxcore.repository.sqlite3_dao import SQLite3DAO

import config


class FeedDao(SQLite3DAO):

    def __init__(self, auto_commit=True):
        super().__init__(
            db_path=config.DB_PATH, table_name="feed", auto_commit=auto_commit
        )

    def create_schema(self):
        """
        Creates the database table for feeds if it doesn't already exist.
        """
        self.ddl(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                slug TEXT,
                provider TEXT,
                type TEXT,
                source TEXT,
                description TEXT,
                format TEXT,
                update_interval TEXT,
                updated_on TEXT,
                risk_score INTEGER,
                geo_score INTEGER,
                data_json TEXT
            );
        """
        )
        try:
            self.ddl(f"ALTER TABLE {self.table_name} ADD COLUMN geo_score INTEGER;")
        except Exception:
            pass
        self.ddl(
            f"CREATE INDEX IF NOT EXISTS idx_feed_type ON {self.table_name} (type);"
        )
        self.ddl(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_feed_slug ON {self.table_name} (slug);"
        )

    def from_dict(self, vo):
        """
        Converts a dictionary to a format suitable for database insertion,
        specifically handling datetime conversion for 'updated_on'.

        Args:
            vo (dict): The dictionary to convert.

        Returns:
            dict: The converted dictionary.
        """
        vo = dict(vo)
        if "_id" in vo:
            vo.pop("_id", None)
        vo["updated_on"] = datetime.now(timezone.utc).isoformat()
        if "data" in vo:
            data = vo.pop("data")
            if data is not None:
                vo["data_json"] = json.dumps(data, ensure_ascii=False)
            else:
                vo["data_json"] = None

        valid_columns = {
            "name", "slug", "provider", "type", "source", "description",
            "format", "update_interval", "updated_on", "risk_score",
            "geo_score", "data_json"
        }
        filtered = {k: v for k, v in vo.items() if k in valid_columns}
        return super().from_dict(filtered)

    def update_by_id(self, id: int, vo: dict):
        vo = self.from_dict(vo)
        return super().update_by_id(id, vo)

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
            if isinstance(row["updated_on"], str):
                try:
                    row.update(
                        {"updated_on": datetime.fromisoformat(row["updated_on"])}
                    )
                except Exception:
                    pass
        if "data_json" in row and row["data_json"] is not None:
            try:
                row.update({"data": json.loads(row.pop("data_json"))})
            except Exception:
                row["data"] = []

        return row

    def get_all_by_type(self, types=None, pagination=None) -> list[dict]:
        """
        Get all feeds by type with pagination.

        Args:
            types (list[str]): The types of feeds to retrieve.
            pagination (dict): The pagination parameters.

        Returns:
            list[dict]: The list of feeds.
        """
        if types is None:
            types = ["reputation", "bypass", "geo"]
        sql = (
            f"SELECT "
            f" _id, name, provider, slug, type, source, description, format, update_interval, updated_on, risk_score, geo_score, data_json"
            f" FROM {self.table_name} WHERE type IN ({', '.join(['?'] * len(types))})"
            f" ORDER BY _id DESC"
        )
        count_sql = f"SELECT COUNT(*) AS total FROM {self.table_name} WHERE type IN ({', '.join(['?'] * len(types))})"
        rows = []
        total = self._query(count_sql, params=types, fetch=True)[0]["total"]

        if pagination:
            page = pagination.get("page", 1)
            per_page = pagination.get("per_page", 10)
            offset = (page - 1) * per_page
            sql += f" LIMIT {per_page} OFFSET {offset}"
            pagination["total_elements"] = total
        else:
            pagination = {"total_elements": total, "page": 1, "per_page": total}

        rs = self._query(sql, params=types, fetch=True)
        if rs:
            rows = [self.to_dict(dict(row)) for row in rs]
        return {
            "metadata": pagination,
            "data": rows,
        }
