import ipaddress
from typing import Dict, Any, Optional

from nxcore.middleware.logging import logger
from nxcore.repository.sqlite3_base_dao import SQLite3DAO

import config
from api.tools.network_tool import NetworkTool


class RBLDao(SQLite3DAO):

    def __init__(self, auto_commit=True):
        super().__init__(db_path=config.DB_PATH, table_name="rbl", auto_commit=auto_commit)

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
                feed_type TEXT,
                risk_score INTEGER
            );
        """)
        self.ddl(f"CREATE INDEX IF NOT EXISTS idx_rbl_feed ON {self.table_name} (feed);")
        self.ddl(f"CREATE INDEX IF NOT EXISTS idx_rbl_version_idx ON {self.table_name} (version, idx_s, idx_e);")
        self.ddl(f"CREATE INDEX IF NOT EXISTS idx_rbl_feed_type ON {self.table_name} (feed_type);")

    def get_by_ip(self, ip_str: str):
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
            SELECT
            a.network,
            a.broadcast,
            a.prefix,
            a.version,
            a.feed,
            a.feed_type,
            a.risk_score
            FROM {self.table_name} a
            WHERE idx_s <= ? AND idx_e >= ? AND version = ?
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

    def get_networks_from_feed_type(self, feed_type: str):
        """
        Retrieves a complete record by its feed name.

        Args:
            feed_type (str): The feed type to search for.

        Returns:
            list: A list of network
        """
        query = f"""
            SELECT
            a.network,
            a.broadcast,
            a.prefix,
            a.version,
            a.feed,
            a.feed_type,
            a.risk_score
            FROM {self.table_name} a
            WHERE feed_type = ?
            ORDER BY idx_s
        """
        rs = self._query(query, (feed_type,), fetch=True)
        return rs

    def exists_by_feed(self, feed):
        """
        Retrieves a complete record by its feed name.

        Args:
            feed (str): The feed name to search for.

        Returns:
            bool: True if feed exists, False otherwise.
        """
        sql = f"SELECT 1 FROM {self.table_name} WHERE feed = ? LIMIT 1"
        rs = self._query(sql, (feed,), fetch=True)
        return len(rs) == 1

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
            query = (f"select a.network, a.broadcast, a.prefix,a.version, a.feed, a.risk_score, a.feed_type"
                     f" from {self.table_name} a"
                     f" where a.idx_s <= ? and a.idx_e >= ? and a.version=?")
            return self._query(query, params=(ip_packed, ip_packed, ver), fetch=True)
        except Exception as e:
            logger.error(f"Error finding RBL data for IP {ip_str}: {str(e)}")
            raise
