from flask import render_template, current_app

from api.controllers.ip_controller import routes as ip_routes

routes = [
    (ip_routes, "/api/ip"),
]


def register(app, bp):
    @bp.route("/")
    def index():
        return render_template("index.html")

    @bp.route("/<path:path>")
    def catch_all(path: str):
        if "." in path and not path.endswith("/"):
            try:
                return current_app.send_static_file(path)
            except Exception:
                pass
        return render_template("index.html")

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)
