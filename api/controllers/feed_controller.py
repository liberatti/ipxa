from flask import Blueprint, request, Response
from nxcore.controllers.base_controller import (
    response_data,
    response_error_parse,
    response_error_500,
    get_pagination
)
from marshmallow import ValidationError
from api.repository.feed_model import FeedDao

routes = Blueprint("feed", __name__)


@routes.route("/", methods=["GET"])
def get_all() -> Response:
    """
    Retrieves all feed entries, filtered by reputation and bypass types, with pagination.

    Returns:
        Response: A Flask Response object containing the list of feeds or an error message.
    """
    try:
        with FeedDao() as dao:
            return response_data(dao.get_all_by_type(types=["reputation", "bypass"], pagination=get_pagination()))
    except Exception as e:
        return response_error_500(msg=str(e))


@routes.route("/", methods=["POST"])
def save() -> Response:
    """
    Creates and persists a new feed entry from the request JSON.

    Returns:
        Response: A Flask Response object containing the created feed or an error message.
    """
    try:
        with FeedDao() as dao:
            feed = request.json
            return response_data(dao.persist(feed))
    except ValidationError as err:
        return response_error_parse(err)
    except Exception as e:
        return response_error_500(msg=str(e))


@routes.route("/<int:id>", methods=["PUT"])
def update(id: int) -> Response:
    """
    Updates an existing feed entry identified by ID with the provided request JSON.

    Args:
        id (int): The ID of the feed to update.

    Returns:
        Response: A Flask Response object containing the updated feed or an error message.
    """
    try:
        with FeedDao() as dao:
            feed = request.json
            return response_data(dao.update_by_id(id, feed))
    except Exception as e:
        return response_error_500(msg=str(e))


@routes.route("/<int:id>", methods=["DELETE"])
def remove(id: int) -> Response:
    """
    Removes a feed entry identified by ID.

    Args:
        id (int): The ID of the feed to remove.

    Returns:
        Response: A Flask Response object indicating the result of the deletion or an error message.
    """
    try:
        with FeedDao() as dao:
            return response_data(dao.remove_by_id(id))
    except Exception as e:
        return response_error_500(msg=str(e))
