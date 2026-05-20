
from nxcore.controllers.base_controller import response_ok
from api.repository.rbl_model import RBLModuleDao
from nxcore.controllers.base_controller import (
    response_data,
    response_error_parse,
    response_error_500,
    response_error_401
)
from nxcore.middleware.jwt import (
    jwt_decode,
    jwt_create_access_token,
    jwt_create_refresh_token,
    jwt_get_refresh
)
from flask import Blueprint, request, Response

from config import JWT_EXPIRE

routes = Blueprint("rbl_module", __name__)


@routes.route("/", methods=["POST"])
def add_rbl() -> Response:
    """
    Add a new RBL module.

    Returns:
        Response: A Flask Response object with a success message or an error.
    """
    with RBLModuleDao() as dao:
        data = request.json # {'feeds': ["feed1", "feed2"], 'wid': 1}
        dao.delete_by_wid(data["wid"])
        for feed in data["feeds"]:
            result = dao.persist({"feed": feed, "wid": data["wid"]})
            if not result:
                return response_error_parse(f"Error saving RBL module {feed}")
    return response_ok("Record created")


@routes.route("/<wid>", methods=["DELETE"])
def del_rbl(wid: int) -> Response:
    """
    Delete an RBL module.

    Args:
        wid (int): The id of the RBL module to delete.

    Returns:
        Response: A Flask Response object with a success message or an error.
    """
    with RBLModuleDao() as dao:
        result = dao.get_by_wid(wid)
        if result:
            dao.delete_by_wid(wid)
        else:
            return response_error_500("RBL module not found")
    return response_ok("Record deleted")