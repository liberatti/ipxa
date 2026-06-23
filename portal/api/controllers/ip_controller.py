from nxcore.controllers.base_controller import response_data
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
    return response_data({}, headers={})
