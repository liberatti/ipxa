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
    """
    Retrieves a specific workspace by its ID.

    Args:
        workspace_id (str): The ID of the workspace to retrieve.

    Returns:
        Response: A Flask Response object containing the workspace data or a 404 error.
    """
    with WorkspaceDao() as dao:
        workspace = dao.get_by_id(workspace_id)
        if workspace:
            return response_data(workspace, dao.schema)
        else:
            return response_error_404()


@routes.route("", methods=["POST"])
@has_any_authority(authorities=["superuser"])
def save():
    """
    Creates and persists a new workspace from the request JSON.

    Returns:
        Response: A Flask Response object containing the created workspace or a validation error.
    """
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
    """
    Retrieves a paginated list of all workspaces.

    Returns:
        Response: A Flask Response object containing the list of workspaces.
    """
    with WorkspaceDao() as dao:
        result = dao.get_all(pagination=get_pagination())
        return response_data(result, dao.pageSchema)


@routes.route("/<workspace_id>", methods=["PUT"])
@has_any_authority(authorities=["superuser"])
def update(workspace_id):
    """
    Updates an existing workspace identified by ID with the provided request JSON.

    Args:
        workspace_id (str): The ID of the workspace to update.

    Returns:
        Response: A Flask Response object containing the updated workspace or a validation error.
    """
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
    """
    Deletes a specific workspace by its ID.

    Args:
        workspace_id (str): The ID of the workspace to delete.

    Returns:
        Response: A Flask Response object indicating the result of the deletion or a 404 error.
    """
    with WorkspaceDao() as dao:
        r = dao.delete_by_id(workspace_id)
        if r:
            return response_data_removed(workspace_id)
        else:
            return response_error_404()
