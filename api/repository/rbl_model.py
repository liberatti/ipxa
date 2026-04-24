import ipaddress
from typing import Dict, Any, Optional

from basic4web.middleware.logging import logger
from basic4web.repository.sqlite3_base_dao import SQLite3DAO

import config
from api.tools.network_tool import NetworkTool


class RBLDao(SQLite3DAO):

    def __init__(self):
        super().__init__(db_path=config.DB_PATH, table_name="rbl")

    def create_schema(self):
        """
        Creates the database table for RBL data if it doesn't already exist.
        """
        self.ddl(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                prefix INTEGER,
                version INTEGER,
                network TEXT,
                broadcast TEXT,
                idx_s BLOB,
                idx_e BLOB,
                feed TEXT,
                risk_score INTEGER
            );
        """)

    def get_by_ip(self, ip_str):
        """
        Retrieves all RBL records that contain the given IP address.

        Args:
            ip_str (str): The IP address string.

        Returns:
            list: A list of matching RBL records.
        """
        ip_obj = ipaddress.ip_address(ip_str)
        ip_packed = ip_obj.packed
        ver = 4 if NetworkTool.is_ipv4(ip_str) else 6
        query = (f"""
            SELECT network, broadcast, prefix,version, feed, risk_score
            FROM {self.table_name}
            WHERE idx_s <= ? AND idx_e >= ? and version= ?
            ORDER BY idx_s
        """)

        return self._query(query, params=(ip_packed, ip_packed, ver), fetch=True)

    def delete_by_feed_name(self, feed_name: str) -> None:
        """
        Deletes all RBL records associated with a specific feed.

        Args:
            feed_name (str): The feed name to delete.
        """
        try:
            query = f"DELETE from {self.table_name} where feed = ?"
            return self._query(query, params=(feed_name,), fetch=True)
        except Exception as e:
            logger.error(f"Error deleting RBL data for feed {feed_name}: {str(e)}")
            raise

    def find_by_ip(self, ip_str: str) -> Optional[Dict[str, Any]]:
        """
        Finds RBL information for a given IP address.

        Args:
            ip_str (str): The IP address string.

        Returns:
            Optional[Dict[str, Any]]: The RBL records if found, None otherwise.
        """
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            ip_packed = ip_obj.packed
            ver = 4 if NetworkTool.is_ipv4(ip_str) else 6
            query = (f"select network, broadcast, prefix,version, feed,risk_score"
                     f" from {self.table_name}"
                     f" where idx_s <= ? and idx_e >= ? and version=?")
            return self._query(query, params=(ip_packed, ip_packed, ver), fetch=True)
        except Exception as e:
            logger.error(f"Error finding RBL data for IP {ip_str}: {str(e)}")
            raise
