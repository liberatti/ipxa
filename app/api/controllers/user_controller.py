import bcrypt
from flask import Blueprint, request, Response
from nxcore.controllers.base_controller import (
    response_data,
    response_ok,
    response_error,
    response_error_404,
    has_any_authority,
)
from api.repository.oauth_model import UserDao

routes = Blueprint("users", __name__)


@routes.route("/", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
def get_all_users() -> Response:
    """
    Retrieves all users. Passwords are redacted for security.
    """
    with UserDao() as dao:
        users = dao.get_all()
        for user in users.get("data", []):
            user.pop("password", None)
        return response_data(users)


@routes.route("/<int:id>", methods=["GET"])
@has_any_authority(authorities=["superuser"], _internal=True)
def get_user(id: int) -> Response:
    """
    Retrieves a single user by ID. Password is redacted.
    """
    with UserDao() as dao:
        user = dao.get_by_id(id)
        if not user:
            return response_error_404()
        user.pop("password", None)
        return response_data(user)


@routes.route("/", methods=["POST"])
@has_any_authority(authorities=["superuser"], _internal=True)
def create_user() -> Response:
    """
    Creates a new user. The password is encrypted before saving.
    """
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return response_error("Missing required fields: email and password")

    with UserDao() as dao:
        existing = dao.get_by_email(data["email"])
        if existing:
            return response_error("User with this email already exists")

        raw_password = data.get("password")
        secure_password = bcrypt.hashpw(
            raw_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        user_to_create = {
            "name": data.get("name", "User"),
            "email": data["email"],
            "password": secure_password,
            "role": data.get("role", "user"),
            "service_token": data.get("service_token", ""),
        }

        if dao.persist(user_to_create):
            return response_ok("Record created")

    return response_error("Record not created")


@routes.route("/<int:id>", methods=["PUT"])
@has_any_authority(authorities=["superuser"], _internal=True)
def update_user(id: int) -> Response:
    """
    Updates an existing user.
    """
    data = request.json
    if not data:
        return response_error("Missing update data")

    with UserDao() as dao:
        user = dao.get_by_id(id)
        if not user:
            return response_error_404()

        email = data.get("email")
        if email and email != user["email"]:
            existing = dao.get_by_email(email)
            if existing:
                return response_error("User with this email already exists")
            user["email"] = email

        if "name" in data:
            user["name"] = data["name"]

        if "role" in data:
            user["role"] = data["role"]

        if "service_token" in data:
            user["service_token"] = data["service_token"]

        password = data.get("password")
        if password:
            secure_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user["password"] = secure_password

        dao.update_by_id(id, user)
        return response_ok("Record updated")


@routes.route("/<int:id>", methods=["DELETE"])
@has_any_authority(authorities=["superuser"], _internal=True)
def remove_user(id: int) -> Response:
    """
    Removes a user by ID.
    """
    with UserDao() as dao:
        user = dao.get_by_id(id)
        if not user:
            return response_error_404()
        dao.remove_by_id(id)
    return response_data(True)
