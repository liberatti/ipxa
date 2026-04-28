import traceback

import nxcore.config as nxcore_config
from nxcore.controllers.base_controller import response_error_404, response_error_500
from nxcore.middleware.logging import logger
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_restful import Api

import config
from api.routes import register as register_api_routes

app = Flask(__name__)

cors = CORS(resources={r"/*": {"origins": "*"}})
cors.init_app(app)

ma = Marshmallow()
ma.init_app(app)

api = Api(app)

bp = Blueprint("gw", __name__, template_folder="templates")
register_api_routes(app, bp)
app.register_blueprint(bp)


@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 Not Found errors.
    """
    return response_error_404()


@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 Internal Server errors and logs the stack trace.
    """
    stack_trace = traceback.format_exc()
    logger.error(f"500 Error: {error}, Stack Trace: {stack_trace}")
    return response_error_500("Unexpected Server Error", details=stack_trace)


@app.errorhandler(Exception)
def handle_exception(error):
    """
    Generic exception handler that logs the stack trace and returns a 500 error.
    """
    stack_trace = traceback.format_exc()
    logger.error(f"Internal Server Error: {stack_trace}")
    return response_error_500("Unexpected Server Error", details=stack_trace)


with app.app_context():
    nxcore_config.init(
        {"LOGLEVEL": config.LOGLEVEL}
    )
