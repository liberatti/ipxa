from flask import Blueprint, request
from marshmallow import ValidationError

from api.repository.workspace_model import WorkspaceDao
from nxcore.controllers.base_controller import (
    response_data,
    response_error_404,
    response_error_parse,
    get_pagination,
    has_any_authority,
    response_data_removed
)

routes = Blueprint("workspace", __name__)


@routes.route("/<workspace_id>", methods=["GET"])
@has_any_authority(authorities=["viewer", "superuser"])
def get(workspace_id):
    with WorkspaceDao() as dao:
        workspace = dao.get_by_id(workspace_id)
        if workspace:
            return response_data(workspace, dao.schema)
        else:
            return response_error_404()


@routes.route("", methods=["POST"])
@has_any_authority(authorities=["superuser"])
def save():
    try:
        with WorkspaceDao() as dao:
            vo = dao.json_load(request.json)
            dao.persist(vo)
            return response_data(vo, dao.schema)
    except ValidationError as err:
        return response_error_parse(err)


@routes.route("", methods=["GET"])
@has_any_authority(authorities=["viewer", "superuser"])
def search():
    with WorkspaceDao() as dao:
        result = dao.get_all(pagination=get_pagination())
        return response_data(result, dao.pageSchema)


@routes.route("/<workspace_id>", methods=["PUT"])
@has_any_authority(authorities=["superuser"])
def update(workspace_id):
    try:
        with WorkspaceDao() as dao:
            vo = dao.json_load(request.json)
            result = dao.update_by_id(workspace_id, vo)
            return response_data(result, dao.schema)
    except ValidationError as err:
        return response_error_parse(err)


@routes.route("/<workspace_id>", methods=["DELETE"])
@has_any_authority(authorities=["superuser"])
def delete(workspace_id):
    with WorkspaceDao() as dao:
        r = dao.delete_by_id(workspace_id)
        if r:
            return response_data_removed(workspace_id)
        else:
            return response_error_404()
