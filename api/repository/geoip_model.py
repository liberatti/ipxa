import ipaddress
from typing import Dict, Any, Optional

from nxcore.middleware.logging import logger
from nxcore.repository.sqlite3_base_dao import SQLite3DAO

import config
from api.tools.network_tool import NetworkTool


class GeoIpDao(SQLite3DAO):

    def __init__(self, auto_commit: bool = False):
        super().__init__(db_path=config.DB_PATH, table_name="geoip", auto_commit=auto_commit)

    def create_schema(self):
        """
        Creates the database table for GeoIP data if it doesn't already exist.
        """
        self.ddl(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                ans_number INTEGER,
                ans_description TEXT,
                country_code TEXT,
                source TEXT,
                network TEXT,
                broadcast TEXT,
                idx_s BLOB,
                idx_e BLOB,
                version INTEGER,
                prefix INTEGER
            );
        """)

    def delete_by_source(self, source: str) -> None:
        """
        Deletes all GeoIP records associated with a specific source.

        Args:
            source (str): The source name to delete.
        """
        try:
            query = f"DELETE from {self.table_name} where source = ?"
            return self._query(query, params=(source,), fetch=True)
        except Exception as e:
            logger.error(f"Error deleting GeoIP data for source {source}: {str(e)}")
            raise

    def find_by_ip(self, ip_str: str) -> Optional[Dict[str, Any]]:
        """
        Finds GeoIP information for a given IP address.

        Args:
            ip_str (str): The IP address string to search for.

        Returns:
            Optional[Dict[str, Any]]: The GeoIP record if found, None otherwise.
        """
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            ip_packed = ip_obj.packed
            ver = 4 if NetworkTool.is_ipv4(ip_str) else 6
            query = (f"select "
                     f" ans_number,country_code,ans_description,source,network,broadcast,version,prefix"
                     f" from {self.table_name}"
                     f" where idx_s <= ? and idx_e >= ? and version=? "
                     f" order by prefix desc"
                     f" limit 1")
            r = self._query(query, params=(ip_packed, ip_packed, ver), fetch=True)
            return r[0] if r else None
        except Exception as e:
            logger.error(f"Error finding Geo data for IP {ip_str}: {str(e)}")
            raise
