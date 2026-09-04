import csv
import gzip
import io
import ipaddress
import json
import os
import tarfile
import traceback
from typing import Dict

import requests
from nxcore.middleware.logging_manager import logger

import config
from api.repository.geoip_model import GeoIpDao
from api.repository.rbl_model import RBLDao
from api.tools.network_tool import NetworkTool


def update_maxmind(MAXMIND_ACCOUNT_ID, MAXMIND_LICENSE_KEY):
    """
    Downloads and updates MaxMind GeoLite2-ASN and GeoLite2-City databases.

    Args:
        MAXMIND_ACCOUNT_ID (str): MaxMind account ID.
        MAXMIND_LICENSE_KEY (str): MaxMind license key.
    """
    for edition_id in ["GeoLite2-ASN", "GeoLite2-City"]:
        url = f"https://download.maxmind.com/geoip/databases/{edition_id}/download?suffix=tar.gz"
        response = requests.get(url, auth=(MAXMIND_ACCOUNT_ID, MAXMIND_LICENSE_KEY))
        if response.status_code == 200:
            zip_content = io.BytesIO(response.content)
            with tarfile.open(fileobj=zip_content, mode="r:gz") as tar:
                os.makedirs(config.DB_PATH, exist_ok=True)
                for member in tar.getmembers():
                    if member.name.endswith(".mmdb") and member.isfile():
                        dest_path = os.path.join(
                            config.DB_PATH, os.path.basename(member.name)
                        )
                        extracted = tar.extractfile(member)
                        if extracted is not None:
                            with open(dest_path, "wb") as out_f:
                                out_f.write(extracted.read())
                        break
            logger.info(f"Loaded {edition_id} geoip from MaxMind")
        else:
            logger.error(f"Failed to download {edition_id} {response}")


def update_ipverse(feed: Dict):
    """
    Downloads and processes an IPVerse GeoIP feed.

    Args:
        feed (Dict): The feed configuration dictionary.
    """
    response = requests.get(feed["source"])
    if response.status_code == 200:
        tar_content = io.BytesIO(response.content)
        with tarfile.open(fileobj=tar_content, mode="r:gz") as tar:
            with GeoIpDao(auto_commit=True) as dao:
                dao.delete_by_source(feed["name"])
                batch = []
                count = 0
                for member in tar.getmembers():
                    if (
                        member.name.endswith("aggregated.json")
                        or member.name.endswith("addregated.json")
                    ) and member.isfile():
                        f = tar.extractfile(member)
                        if f:
                            try:
                                content = json.load(f)
                                country = content.get("country", "")
                                country_code = content.get("countryCode", "")
                                prefixes = content.get("prefixes", {})

                                ips = []
                                ips.extend(prefixes.get("ipv4", []))
                                ips.extend(prefixes.get("ipv6", []))

                                for line in ips:
                                    if line.strip() and NetworkTool.is_network(line):
                                        addr = line.split("/")
                                        if len(addr) <= 1:
                                            prefix = (
                                                32 if NetworkTool.is_ipv4(line) else 128
                                            )
                                        else:
                                            prefix = addr[1]

                                        info_n = NetworkTool.extract_network_info(
                                            addr[0], prefix=prefix
                                        )
                                        net = {
                                            "source": feed["name"],
                                            "geo_score": feed["geo_score"],
                                            "country_code": country_code,
                                            "ans_description": country,
                                            "ans_number": 0,
                                        }
                                        net.update(info_n)
                                        batch.append(net)
                                        count += 1

                                        if len(batch) >= 1000:
                                            dao.persist_many(batch)
                                            batch = []
                            except Exception as e:
                                logger.error(
                                    f"Failed to parse JSON member {member.name}: {e}"
                                )
                if batch:
                    dao.persist_many(batch)
                logger.info(f"Loaded {count} geoip records from {feed['name']}")


def update_ip2asn(feed: Dict):
    """
    Downloads and processes an IPtoASN GeoIP feed.

    Args:
        feed (Dict): The feed configuration dictionary.
    """
    src = f"https://iptoasn.com/data/{feed['name']}.tsv.gz"
    response = requests.get(src)
    if response.status_code == 200:
        zip_content = io.BytesIO(response.content)
        with gzip.open(zip_content, "rt", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")
            batch = []
            with GeoIpDao(auto_commit=True) as dao:
                dao.delete_by_source("ip2asn")
                i = 0
                for row in reader:
                    try:
                        p = NetworkTool.calc_prefix_from_range(
                            ipaddress.ip_address(row[0]), ipaddress.ip_address(row[1])
                        )
                        net = NetworkTool.extract_network_info(row[0], prefix=p)
                        r = {
                            "source": "ip2asn",
                            "geo_score": feed["geo_score"],
                            "ans_number": int(row[2]),
                            "country_code": row[3],
                            "ans_description": row[4],
                        }
                        r.update(net)
                        batch.append(r)
                        i += 1
                        if i % 1000 == 0:
                            dao.persist_many(batch)
                            batch = []
                    except Exception:
                        logger.error(traceback.format_exc())
                dao.persist_many(batch)
                logger.info(f"Loaded {i} geoip records from {feed['name']}")


def update_ipinfo(IPINFO_TOKEN: str, feed: Dict):
    """
    Downloads and processes an IPInfo Lite feed.

    Args:
        feed (Dict): The feed configuration dictionary.
    """
    src = f"https://ipinfo.io/data/ipinfo_lite.csv.gz?&token={IPINFO_TOKEN}"
    response = requests.get(src)
    if response.status_code == 200:
        zip_content = io.BytesIO(response.content)
        with gzip.open(zip_content, "rt", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            batch = []
            with GeoIpDao(auto_commit=True) as dao:
                dao.delete_by_source("ipinfo")
                i = 0
                for row in reader:
                    try:
                        network_str = row.get("network")
                        if not network_str:
                            continue

                        addr_parts = network_str.split("/")
                        addr = addr_parts[0]
                        if len(addr_parts) <= 1:
                            prefix = 32 if NetworkTool.is_ipv4(addr) else 128
                        else:
                            prefix = int(addr_parts[1])

                        net = NetworkTool.extract_network_info(addr, prefix=prefix)

                        asn_str = row.get("asn")
                        asn_num = 0
                        if asn_str:
                            digits = "".join(filter(str.isdigit, str(asn_str)))
                            if digits:
                                asn_num = int(digits)

                        r = {
                            "source": "ipinfo",
                            "geo_score": feed["geo_score"],
                            "ans_number": asn_num,
                            "country_code": row.get("country_code") or "",
                            "ans_description": row.get("as_name") or "",
                        }
                        r.update(net)
                        batch.append(r)
                        i += 1
                        if i % 1000 == 0:
                            # logger.info(f"Processing {i} records from ipinfo")
                            dao.persist_many(batch)
                            batch = []
                    except Exception:
                        logger.error(traceback.format_exc())
                if batch:
                    dao.persist_many(batch)
                logger.info(f"Loaded {i} geoip records from ipinfo")
    else:
        logger.warning(f"ipinfo download failed. {response.status_code}")


def update_feed(feed):
    """
    Downloads and processes a standard IP blocklist feed.

    Args:
        feed (dict): The feed configuration dictionary.
    """
    if not feed:
        return

    feed_name = feed.get("name")
    if not feed_name:
        return

    with RBLDao() as dao:
        dao.delete_by_feed_name(feed_name)

    lines = []
    feed_format = feed.get("format", "")
    if "embedded" in feed_format:
        raw_data = feed.get("data") or []
        if isinstance(raw_data, list):
            lines = raw_data
        elif isinstance(raw_data, str):
            lines = raw_data.splitlines()
    elif feed.get("source"):
        source_url = feed["source"]
        if "iblocklist" in feed.get("provider", ""):
            if config.IBLOCKLIST_USERNAME and config.IBLOCKLIST_PASSWORD:
                source_url = f"{source_url}&username={config.IBLOCKLIST_USERNAME}&pin={config.IBLOCKLIST_PASSWORD}"
            else:
                logger.warning(f"Feed {feed_name} skipped, no credentials")
                return
        try:
            resp = requests.get(source_url, timeout=10)
            if resp and resp.status_code == 200:
                if "cdir_text" in feed_format:
                    lines = resp.text.splitlines()
                elif "cdir_gz" in feed_format:
                    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
                        for gzl in gz:
                            lines.append(gzl.decode("utf-8").strip())
        except Exception as e:
            logger.error(f"Failed to fetch feed {feed_name} from {source_url}: {e}")
            return
    else:
        logger.warning(f"Feed {feed_name} skipped, no source or embedded data")
        return

    with RBLDao() as dao:
        batch = []
        i = 0
        for line in lines:
            t = str(line).strip()
            if t and not t.startswith("#"):
                net = build_ip_info(t, feed)
                if net:
                    batch.append(net)
                    i += 1
            if len(batch) >= 500:
                dao.persist_many(batch)
                batch = []
        if batch:
            dao.persist_many(batch)
        logger.info(f"Loaded {i} records from {feed_name}")


def build_ip_info(line: str, feed: Dict):
    if NetworkTool.is_network(line):
        addr = line.split("/")
        net = {
            "feed": feed["name"],
            "risk_score": feed.get("risk_score", 0),
            "feed_type": feed.get("type", None),
        }
        if len(addr) <= 1:
            addr.append(32)
        info_n = NetworkTool.extract_network_info(addr[0], prefix=addr[1])
        net.update(info_n)
        return net
    return None
