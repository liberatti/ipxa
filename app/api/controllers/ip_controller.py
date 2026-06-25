import os

from nxcore.controllers.base_controller import response_data, has_any_authority
from flask import Blueprint, Response
from geoip2 import database

import config
from api.repository.geoip_model import GeoIpDao
from api.repository.rbl_model import RBLDao
from api.tools.common import enrich_country, cached
from api.tools.network_tool import NetworkTool
from config import cache

routes = Blueprint("ip", __name__)


def _fill_org(info: dict) -> dict:
    """
    Fills the organization information.

    Args:
        info (dict): The IP information dictionary.

    Returns:
        dict: The IP information dictionary with organization information filled.
    """
    org = {}
    geoip = info["location"]
    if geoip:
        org.update(
            {
                "asn_number": geoip.pop("ans_number", ""),
                "asn_name": geoip.pop("ans_description", ""),
                "asn_description": geoip.pop("ans_description", ""),
            }
        )
    else:
        geoip.pop("ans_number", None)
        geoip.pop("ans_description", None)
    info.update({"organization": org})


def _fill_geo(info: dict) -> dict:
    """
    Fills the GeoIP information.

    Args:
        info (dict): The IP information dictionary.

    Returns:
        dict: The IP information dictionary with GeoIP information filled.
    """
    geoip = {}
    ip = info["ip"]["address"]
    try:
        with GeoIpDao() as dao:
            row = dao.find_by_ip(ip)
            if row:
                geoip.update(row)
    except Exception:
        pass

    for db_name in ["ASN", "City"]:
        db_file = f"{config.DB_PATH}/GeoLite2-{db_name}.mmdb"
        if os.path.exists(db_file):
            with database.Reader(db_file) as reader:
                try:
                    if db_name == "ASN":
                        r_asn = reader.asn(ip)
                        info["organization"].update(
                            {
                                "asn_number": r_asn.autonomous_system_number,
                                "asn_name": r_asn.autonomous_system_organization,
                                "asn_description": r_asn.autonomous_system_organization,
                            }
                        )
                    elif db_name == "City":
                        r_city = reader.city(ip)
                        geoip.update(
                            {
                                "country_code": r_city.country.iso_code,
                                "country": r_city.country.name,
                                "region": (
                                    r_city.subdivisions.most_specific.name
                                    if r_city.subdivisions
                                    else None
                                ),
                                "city": r_city.city.name,
                                "latitude": r_city.location.latitude,
                                "longitude": r_city.location.longitude,
                            }
                        )
                except Exception:
                    pass

    if geoip:
        info["ip"].update(
            {
                "version": geoip.pop("version", None),
                "broadcast": geoip.pop("broadcast", None),
                "network": geoip.pop("network", None),
                "prefix": geoip.pop("prefix", None),
            }
        )

        for field in ["source", "idx_s", "idx_e"]:
            geoip.pop(field, None)

        enrich_country(geoip)
        info.update({"location": geoip})


def _build_ip_info(ip: str) -> dict:
    """
    Builds the IP information dictionary.

    Args:
        ip (str): The IP address to query.

    Returns:
        dict: The IP information dictionary.
    """
    ipd = {"address": ip}

    rep = {
        "reasons": [],
        "risk_score": 0,
        "trusted": False,
    }

    try:
        with RBLDao() as dao:
            rep_data = dao.get_by_ip(ip)
            if rep_data:
                for r in rep_data:
                    feed = r.get("feed", "")
                    feed_type = r.get("feed_type", None)
                    if "bypass" in feed_type:
                        rep["trusted"] = True
                        rep["reasons"].append(f"trust:{feed}")
                    else:
                        rep["reasons"].append(f"rbl:{feed}")
                        rep["risk_score"] += r.get("risk_score", 0)
    except Exception:
        pass

    net_info = NetworkTool.extract_network_info(ip, prefix=32)
    net_info.pop("idx_s", None)
    net_info.pop("idx_e", None)
    ipd.update(net_info)

    return {
        "ip": ipd,
        "security": rep,
    }


@routes.route("/info/<ip>", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
@cached("i")
def ip_info(ip: str) -> Response:
    """
    Retrieves comprehensive GeoIP, ASN, and reputation data for a specific IP address.

    Args:
        ip (str): The IP address to query.
    Returns:
        Response: A Flask Response object containing the IP information.
    """
    info = _build_ip_info(ip)
    _fill_geo(info)
    _fill_org(info)
    cache[f"i:{ip}"] = info
    headers = {
        "x-risk-score": info["security"]["risk_score"],
        "x-cache": "miss",
        "x-country-code": info["location"]["country_code"],
        "x-trusted": info["security"]["trusted"],
    }
    return response_data(info, headers=headers)


@routes.route("/check/<ip>", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
@cached("c")
def ip_check(ip: str) -> Response:
    """
    Returns a summary risk assessment for the IP.

    Args:
        ip (str): The IP address to query.

    Returns:
        Response: A Flask Response object containing the IP information.
    """
    info = _build_ip_info(ip)
    security = info.get("security", {})
    risk_score = security.get("risk_score", 0)
    reasons = security.get("reasons", [])

    result = {"ip": ip, "risk_score": risk_score, "reasons": reasons}
    cache[f"c:{ip}"] = result
    headers = {
        "x-risk-score": security.get("risk_score", 0),
        "x-cache": "miss",
        "x-trusted": info["security"]["trusted"],
    }
    return response_data(result, headers=headers)


@routes.route("/quick/<ip>", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
@cached("q")
def ip_quick(ip: str) -> Response:
    """
    Returns only the risk_score for quick decisions (e.g., firewall).

    Args:
        ip (str): The IP address to query.

    Returns:
        Response: A Flask Response object containing the IP information.
    """
    info = _build_ip_info(ip)
    security = info.get("security", {})
    result = {"risk_score": security.get("risk_score", 0)}
    cache[f"q:{ip}"] = result
    headers = {
        "x-risk-score": security.get("risk_score", 0),
        "x-cache": "miss",
        "x-trusted": info["security"]["trusted"],
    }
    return response_data(result, headers=headers)
