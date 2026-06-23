from flask import Blueprint, request, Response
from nxcore.controllers.base_controller import (
    response_data,
    response_ok,
    get_pagination,
    response_error,
)
from nxcore.controllers.base_controller import has_any_authority
from api.repository.feed_model import FeedDao
from api.repository.rbl_model import RBLDao
from api.tools.feed_tool import update_feed

routes = Blueprint("feed", __name__)


@routes.route("/", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
def get_all() -> Response:
    """
    Retrieves all feed entries, filtered by reputation and bypass types,
    with pagination.

    Returns:
        Response: A Flask Response object containing the list of feeds
        or an error message.
    """
    types = ["reputation", "bypass"]
    if "type" in request.args:
        types = [request.args.get("type")]

    with FeedDao() as dao:
        return response_data(
            dao.get_all_by_type(types=types, pagination=get_pagination())
        )


@routes.route("/", methods=["POST"])
@has_any_authority(authorities=["superuser"], _internal=True)
def save() -> Response:
    """
    Creates and persists a new feed entry from the request JSON.

    Returns:
        Response: A Flask Response object containing the created feed
        or an error message.
    """
    feed = request.json
    with FeedDao(auto_commit=False) as dao:
        if dao.persist(feed):
            update_feed(feed)
            dao.commit()
            return response_ok("Record created")
        dao.rollback()
    return response_error("Record not created")


@routes.route("/<int:id>", methods=["PUT"])
@has_any_authority(authorities=["superuser"], _internal=True)
def update(id: int) -> Response:
    """
    Updates an existing feed entry identified by ID with the provided
    request JSON.

    Args:
        id (int): The ID of the feed to update.

    Returns:
        Response: A Flask Response object containing the updated feed
        or an error message.
    """
    feed = request.json
    update_feed(feed)
    with FeedDao() as dao:
        dao.update_by_id(id, feed)
    return response_ok("Record updated")


@routes.route("/<int:id>", methods=["DELETE"])
@has_any_authority(authorities=["superuser"], _internal=True)
def remove(id: int) -> Response:
    """
    Removes a feed entry identified by ID.

    Args:
        id (int): The ID of the feed to remove.

    Returns:
        Response: A Flask Response object indicating the result of
        the deletion or an error message.
    """
    with FeedDao(auto_commit=False) as dao:
        feed = dao.get_by_id(id)
        if feed:
            dao.remove_by_id(id)
            with RBLDao() as rbl_dao:
                rbl_dao.delete_by_feed_name(feed["name"])
            dao.commit()
    return response_data(True)
