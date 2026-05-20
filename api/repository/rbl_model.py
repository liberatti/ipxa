import ipaddress
from typing import Dict, Any, Optional

from nxcore.middleware.logging import logger
from nxcore.repository.sqlite3_base_dao import SQLite3DAO

import config
from api.tools.network_tool import NetworkTool

class RBLModuleDao(SQLite3DAO):

    def __init__(self, auto_commit=True):
        super().__init__(db_path=config.DB_PATH, table_name="rbl_module", auto_commit=auto_commit)

    def create_schema(self):
        """
        Creates the database table for RBL data if it doesn't already exist.
        """
        self.ddl(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                feed text,
                wid integer
            );
        """)

    def get_by_wid(self, wid: int) -> Optional[Dict[str, Any]]:
        """
        Finds RBL information for a given wid.

        Args:
            wid (int): The wid to search for.

        Returns:
            Optional[Dict[str, Any]]: The RBL records if found, None otherwise.
        """
        try:
            query = (f"select * from {self.table_name} a"
                     f" where a.wid=?")
            return self._query(query, params=(wid,), fetch=True)
        except Exception as e:
            logger.error(f"Error finding RBL data for wid {wid}: {str(e)}")
            raise
        
    def delete_by_wid(self, wid: int) -> None:
        """
        Deletes all RBL records associated with a specific feed.

        Args:
            wid (int): The wid to delete.
        """
        try:
            query = f"DELETE from {self.table_name} where wid = ?"
            return self._query(query, params=(wid,), fetch=True)
        except Exception as e:
            logger.error(f"Error deleting RBL data for wid {wid}: {str(e)}")
            raise

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

    def get_by_ip(self, ip_str: str, wid: int = 0):
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
            LEFT JOIN rbl_module b ON a.feed = b.feed
            WHERE idx_s <= ? AND idx_e >= ? AND version = ? and b.wid =?
            ORDER BY idx_s
        """)

        return self._query(query, params=(ip_packed, ip_packed, ver, wid), fetch=True)

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

    def get_networks_from_feed_type(self, feed_type: str, wid: int = 0):
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
            LEFT JOIN rbl_module b ON a.feed = b.feed
            WHERE feed_type = ? and b.wid = ?
            ORDER BY idx_s
        """
        rs = self._query(query, (feed_type, wid), fetch=True)
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

    def find_by_ip(self, ip_str: str, wid: int = 0) -> Optional[Dict[str, Any]]:
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
                     f" left join rbl_module b on a.feed = b.feed"
                     f" where a.idx_s <= ? and a.idx_e >= ? and a.version=? and b.wid=?")
            return self._query(query, params=(ip_packed, ip_packed, ver, wid), fetch=True)
        except Exception as e:
            logger.error(f"Error finding RBL data for IP {ip_str}: {str(e)}")
            raise
