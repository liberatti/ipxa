import sqlite3
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


@routes.route("", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
def get_all() -> Response:
    """
    Retrieves all feed entries, filtered by reputation and bypass types,
    with pagination.

    Returns:
        Response: A Flask Response object containing the list of feeds
        or an error message.
    """
    types = ["reputation", "bypass", "geo"]
    if "type" in request.args:
        types = [request.args.get("type")]

    with FeedDao() as dao:
        return response_data(
            dao.get_all_by_type(types=types, pagination=get_pagination())
        )


@routes.route("/<string:name>", methods=["GET"])
def get_by_name(name: str) -> Response:
    """
    Retrieves a feed by name or slug and returns it in plain text format (txt),
    with metadata attributes commented with '#' and the feed IP/CIDR contents.

    Args:
        name (str): The name or slug of the feed.

    Returns:
        Response: Plain text response containing feed metadata comments and content.
    """
    with FeedDao() as dao:
        feed = dao.get_by_name(name)

    if not feed:
        return Response("Feed not found", status=404, mimetype="text/plain")

    lines = []
    attributes = [
        "name",
        "slug",
        "provider",
        "type",
        "format",
        "source",
        "update_interval",
        "updated_on",
        "risk_score",
        "geo_score",
        "description",
    ]
    for attr in attributes:
        val = feed.get(attr)
        if val is not None and val != "":
            lines.append(f"# {attr}: {val}")

    data = feed.get("data")
    if data:
        if isinstance(data, list):
            for item in data:
                lines.append(str(item))
        elif isinstance(data, str):
            lines.extend(data.splitlines())
    else:
        with RBLDao() as rbl_dao:
            rs = rbl_dao._query(
                "SELECT network, prefix FROM rbl WHERE feed = ? ORDER BY network",
                params=(feed.get("name"),),
                fetch=True,
            )
            if rs:
                for r in rs:
                    lines.append(f"{r['network']}/{r['prefix']}")

    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@routes.route("", methods=["POST"])
@has_any_authority(authorities=["superuser"], _internal=True)
def save() -> Response:
    """
    Creates and persists a new feed entry from the request JSON.

    Returns:
        Response: A Flask Response object containing the created feed
        or an error message.
    """
    feed = request.json
    try:
        with FeedDao(auto_commit=True) as dao:
            if dao.persist(feed):
                try:
                    update_feed(feed)
                except Exception:
                    pass
                return response_ok("Record created")
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: feed.slug" in str(e):
            return response_error("A feed with this slug already exists.")
        if "UNIQUE constraint failed: feed.name" in str(e):
            return response_error("A feed with this name already exists.")
        return response_error(f"Database constraint error: {e}")
    except Exception as e:
        return response_error(f"Failed to create feed: {e}")
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
    try:
        with FeedDao(auto_commit=True) as dao:
            dao.update_by_id(id, feed)
        try:
            update_feed(feed)
        except Exception:
            pass
        return response_ok("Record updated")
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: feed.slug" in str(e):
            return response_error("A feed with this slug already exists.")
        if "UNIQUE constraint failed: feed.name" in str(e):
            return response_error("A feed with this name already exists.")
        return response_error(f"Database constraint error: {e}")
    except Exception as e:
        return response_error(f"Failed to update feed: {e}")


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
    feed_name = None
    with FeedDao(auto_commit=True) as dao:
        feed = dao.get_by_id(id)
        if feed:
            feed_name = feed.get("name")
            dao.delete_by_id(id)

    if feed_name:
        try:
            with RBLDao(auto_commit=True) as rbl_dao:
                rbl_dao.delete_by_feed_name(feed_name)
        except Exception:
            pass

    return response_data(True)
