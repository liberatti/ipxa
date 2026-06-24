import requests

import config
from nxcore.controllers.base_controller import response_data, response_error
from flask import Blueprint, Response

routes = Blueprint("ip", __name__)


@routes.route("/info/<ip>", methods=["GET"])
def ip_info(ip: str) -> Response:
    """
    Retrieves comprehensive GeoIP, ASN, and reputation data for a specific IP address.

    Args:
        ip (str): The IP address to query.
    Returns:
        Response: A Flask Response object containing the IP information.
    """
    url = f"{config.IPXA_API_URL}/api/ip/info/{ip}"
    headers = {"x-api-key": config.IPXA_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return response_data(data)
        else:
            try:
                err_data = response.json()
                msg = err_data.get("message", "Error calling IP API")
            except Exception:
                msg = f"Error calling IP API: {response.status_code}"
            return response_error(msg)
    except Exception as e:
        return response_error(f"Failed to query IP info: {str(e)}")
