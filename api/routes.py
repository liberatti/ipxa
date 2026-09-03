from flask import render_template, current_app
from nxcore.controllers.base_controller import response_error_404
import config
from api.controllers.ip_controller import routes as ip_routes
from api.controllers.oauth_controller import routes as oauth_routes
from api.controllers.feed_controller import routes as feed_routes
from api.controllers.config_controller import routes as config_routes

routes = [
    (ip_routes, f"{config.APP_CONTEXT}/api/ip"),
    (oauth_routes, f"{config.APP_CONTEXT}/api/oauth"),
    (feed_routes, f"{config.APP_CONTEXT}/api/feed"),
    (config_routes, f"{config.APP_CONTEXT}/api/config"),
]


def register(app, bp):
    """
    Register all API routes with the Flask application.

    Args:
        app (Flask): The main Flask application instance.
        bp (Blueprint): The main Blueprint for API routes.
    """

    @bp.route("/")
    def index():
        """
        Serve the main index page.
        """
        return render_template("index.html")

    @bp.route("/<path:path>")
    def catch_all(path: str):
        """
        Handle requests to any path by serving the index page,
        unless it's a request for a static file with an extension or an API route.
        """
        api_prefix = config.APP_CONTEXT.lstrip("/") + "/api" if config.APP_CONTEXT else "api"
        if path.startswith(api_prefix) or path.startswith("api"):
            return response_error_404()

        if "." in path and not path.endswith("/"):
            try:
                return current_app.send_static_file(path)
            except Exception:
                pass
        return render_template("index.html")

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)
