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
from basic4web.middleware.logging import logger

import config
from api.repository.geoip_model import GeoIpDao
from api.repository.rbl_model import RBLDao
from api.tools.network_tool import NetworkTool


# TODO Add support to https://ipinfo.io/dashboard/lite

def update_maxmind(MAXMIND_ACCOUNT_ID, MAXMIND_LICENSE_KEY):
    """
    Downloads and updates MaxMind GeoLite2-ASN and GeoLite2-City databases.

    Args:
        MAXMIND_ACCOUNT_ID (str): MaxMind account ID.
        MAXMIND_LICENSE_KEY (str): MaxMind license key.
    """
    for edition_id in ["GeoLite2-ASN", "GeoLite2-City"]:
        url = f"https://download.maxmind.com/geoip/databases/{edition_id}/download?suffix=tar.gz"
        response = requests.get(
            url, auth=(MAXMIND_ACCOUNT_ID, MAXMIND_LICENSE_KEY)
        )
        if response.status_code == 200:
            zip_content = io.BytesIO(response.content)
            with tarfile.open(fileobj=zip_content, mode="r:gz") as tar:
                os.makedirs(config.DB_PATH, exist_ok=True)
                for member in tar.getmembers():
                    if member.name.endswith(".mmdb") and member.isfile():
                        dest_path = os.path.join(config.DB_PATH, os.path.basename(member.name))
                        extracted = tar.extractfile(member)
                        if extracted is not None:
                            with open(dest_path, "wb") as out_f:
                                out_f.write(extracted.read())
                        break
            logger.info(f"[update] Download {edition_id}")
        else:
            logger.error(f"Failed to download {edition_id} {response}")


def update_feed(feed):
    """
    Downloads and processes a standard IP blocklist feed.

    Args:
        feed (dict): The feed configuration dictionary.
    """
    try:
        logger.info(f"Feed: {feed['name']}")
        source_url = feed["source"]
        if feed["restricted"]:
            if "iblocklist" in feed["provider"]:
                if config.IBLOCKLIST_USERNAME:
                    source_url = f"{source_url}&username={config.IBLOCKLIST_USERNAME}&pin={config.IBLOCKLIST_PASSWORD}"
                else:
                    logger.info(
                        f"Feed {feed['name']} skipped, no credentials"
                    )
        resp = requests.get(source_url, timeout=10)
        if resp and resp.status_code == 200:
            with RBLDao() as dao:
                dao.delete_by_feed_name(feed["name"])
                lines = []
                if "cdir_text" in feed["format"]:
                    lines = resp.text.splitlines()
                if "cdir_gz" in feed["format"]:
                    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
                        for gzl in gz:
                            lines.append(gzl.decode("utf-8").strip())

                batch = []
                i = 0
                for line in lines:
                    if line.strip() and "#" not in line:
                        if NetworkTool.is_network(line):
                            addr = line.split("/")
                            net = {"feed": feed["name"], "cls": feed["action"]}
                            if len(addr) <= 1:
                                addr.append(32)
                            info_n = NetworkTool.extract_network_info(
                                addr[0], prefix=addr[1]
                            )
                            net.update(info_n)
                            batch.append(net)
                            i += 1
                    if i % 500 == 0:
                        dao.persist_many(batch)
                        batch = []
                dao.persist_many(batch)
                logger.info(f"Loaded {i} records from {source_url}")
    except Exception as e:
        logger.error(f"Failed to load {feed['slug']}: %s", e)
        logger.error(traceback.format_exc())


def update_ipverse(feed: Dict):
    """
    Downloads and processes an IPVerse GeoIP feed.

    Args:
        feed (Dict): The feed configuration dictionary.
    """
    response = requests.get(feed["source"])
    if response.status_code == 200:
        logger.info(f"GeoIP (IPVerse): {feed['name']}")
        tar_content = io.BytesIO(response.content)
        with tarfile.open(fileobj=tar_content, mode="r:gz") as tar:
            with GeoIpDao(auto_commit=True) as dao:
                dao.delete_by_source(feed["name"])
                batch = []
                count = 0
                for member in tar.getmembers():
                    if (member.name.endswith("aggregated.json") or member.name.endswith("addregated.json")) and member.isfile():
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
                                            prefix = 32 if NetworkTool.is_ipv4(line) else 128
                                        else:
                                            prefix = addr[1]

                                        info_n = NetworkTool.extract_network_info(
                                            addr[0], prefix=prefix
                                        )
                                        net = {
                                            "source": feed["name"],
                                            "country_code": country_code,
                                            "ans_description": country,
                                            "ans_number": 0
                                        }
                                        net.update(info_n)
                                        batch.append(net)
                                        count += 1

                                        if len(batch) >= 500:
                                            dao.persist_many(batch)
                                            batch = []
                            except Exception as e:
                                logger.error(f"Failed to parse JSON member {member.name}: {e}")
                if batch:
                    dao.persist_many(batch)
                logger.info(f"Loaded {count} records from IPVerse feed {feed['name']}")


def update_ip2asn(feed: Dict):
    """
    Downloads and processes an IPtoASN GeoIP feed.

    Args:
        feed (Dict): The feed configuration dictionary.
    """
    src = f"https://iptoasn.com/data/{feed['name']}.tsv.gz"
    response = requests.get(src)
    if response.status_code == 200:
        logger.info(f"GeoIP: {feed['name']}")
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
                            "ans_number": int(row[2]),
                            "country_code": row[3],
                            "ans_description": row[4],
                        }
                        r.update(net)
                        batch.append(r)
                        i += 1
                        if i % 10000 == 0:
                            dao.persist_many(batch)
                            batch = []
                    except Exception:
                        logger.error(traceback.format_exc())
                dao.persist_many(batch)
            logger.info(f"Load {i} records from {src}")
