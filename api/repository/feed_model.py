from datetime import datetime
import json
from nxcore.repository.sqlite3_base_dao import SQLite3DAO

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
                source TEXT,
                description TEXT,
                format TEXT,
                update_interval TEXT,
                updated_on TEXT,
                risk_score INTEGER,
                data_json TEXT
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
        if "data" in vo:
            vo.update({"data_json": json.dumps(vo.pop("data"), ensure_ascii=False)})

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
        if "data_json" in row and row["data_json"] is not None:
            row.update({"data": json.loads(row.pop("data_json"))})

        return row

    def get_all_by_type(self, types=['reputation', 'bypass'], pagination=None) -> list[dict]:
        sql = (f"select "
                     f" _id,name,provider,slug,type,restricted,source,description,format,update_interval,updated_on,risk_score,data_json"
                     f" from {self.table_name} where type IN ({', '.join(['?'] * len(types))})"
                     f" order by _id asc")
        count_sql = f"SELECT COUNT(*) AS total FROM {self.table_name} where type IN ({', '.join(['?'] * len(types))})"
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
            rows = [row for row in rs]
            for r in rows:
                self.to_dict(r)
        return {
            "metadata": pagination,
            "data": rows,
        }
    
