from flask import Blueprint, request, Response
from nxcore.controllers.base_controller import (
    response_data,
    response_error_parse,
    response_error_500,
    response_error_401,
    get_pagination
)
from marshmallow import ValidationError
from api.repository.feed_model import FeedDao

routes = Blueprint("feed", __name__)

@routes.route("/", methods=["GET"])
def get_all() -> Response:
    try:
        with FeedDao() as dao:
            return response_data(dao.get_all_by_type(pagination=get_pagination()))
    except Exception as e:
        return response_error_500(msg=str(e))

@routes.route("/", methods=["POST"])
def save() -> Response:
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
    try:
        with FeedDao() as dao:
            feed = request.json
            return response_data(dao.update_by_id(id, feed))
    except Exception as e:
        return response_error_500(msg=str(e))

@routes.route("/<int:id>", methods=["DELETE"])
def remove(id: int) -> Response:
    try:
        with FeedDao() as dao:
            return response_data(dao.remove_by_id(id))
    except Exception as e:
        return response_error_500(msg=str(e))
