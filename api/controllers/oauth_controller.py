import traceback
from typing import Dict

import bcrypt
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
from marshmallow import ValidationError

from api.repository.oauth_model import OIDCToken, UserDao
from config import JWT_EXPIRE

routes = Blueprint("oauth", __name__)


@routes.route("/401", methods=["GET"])
def forbidden() -> Response:
    """
    Returns a 401 Unauthorized error response.

    Returns:
        Response: A Flask Response object with a 401 status code.
    """
    return response_error_401()


@routes.route("/token", methods=["GET"])
def refresh_token() -> Response:
    """
    Refreshes the access token using a valid refresh token from the request.

    Returns:
        Response: A Flask Response object containing the new access token or an error message.
    """
    r_token = jwt_get_refresh()
    try:
        payload = jwt_decode(r_token)
        with UserDao() as dao:
            user = dao.get_by_id(payload["sub"])
        if not user:
            return response_error_500(msg=f"Authorization failed for {payload['sub']}")

        return response_data(
            {
                "access_token": jwt_create_access_token(user["_id"], authorities=[user["role"]], profile=user),
                "expires_in": JWT_EXPIRE,
                "token_type": 'bearer'
            }
        )
    except Exception:
        return response_error_500(msg=f"Authorization failed for {r_token}", details=traceback.format_exc())


@routes.route("/login", methods=["POST"])
def login() -> Response:
    """
    Authenticates a user with email and password and returns OIDC tokens.

    Returns:
        Response: A Flask Response object containing the OIDC tokens or an error message.
    """
    try:
        with UserDao() as dao:
            user_dict = dao.json_load(request.json)
            user = dao.get_by_email(user_dict["email"])
            if user and bcrypt.checkpw(
                    user_dict["password"].encode("utf8"),
                    user["password"].encode("utf8")
            ):
                return response_data(_create_oidc_token(user), schema=OIDCToken())

            return response_error_401("Sign in failed")
    except ValidationError as err:
        return response_error_parse(err)


def _create_oidc_token(user: Dict) -> Dict:
    """
    Creates an OIDC token dictionary for a given user.

    Args:
        user (Dict): The user dictionary.

    Returns:
        Dict: A dictionary containing access and refresh tokens, expiration time, and token type.
    """
    if "password" in user:
        user.pop("password")
    return {
        "access_token": jwt_create_access_token(user["_id"], authorities=[user['role']], profile=user),
        "refresh_token": jwt_create_refresh_token(user['_id'] if '_id' in user else user['email']),
        "expires_in": JWT_EXPIRE,
        "token_type": 'bearer'
    }
