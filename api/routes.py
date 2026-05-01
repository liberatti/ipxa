from flask import render_template, current_app

from api.controllers.ip_controller import routes as ip_routes
from api.controllers.oauth_controller import routes as oauth_routes
from api.controllers.workspace_controller import routes as workspace_routes
from api.controllers.feed_controller import routes as feed_routes

routes = [
    (ip_routes, "/api/ip"),
    (oauth_routes, "/api/oauth"),
    (workspace_routes, "/api/workspace"),
    (feed_routes, "/api/feed"),
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
        unless it's a request for a static file with an extension.
        """
        if "." in path and not path.endswith("/"):
            try:
                return current_app.send_static_file(path)
            except Exception:
                pass
        return render_template("index.html")

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)
