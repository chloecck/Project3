from flask import Flask, Request
from werkzeug.exceptions import HTTPException


def _register_before_request(app: Flask, request: Request) -> None:
    @app.before_request
    def log_request_body():
        app.logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
        app.logger.info(f"Body: {request.get_data(as_text=True)}")


def _register_errorhandlers(
    app: Flask,
) -> None:
    @app.errorhandler(AssertionError)
    def handle_AssertionError(error):
        app.logger.error(error)
        return {"err": str(error)}, 400

    @app.errorhandler(ValueError)
    def handle_ValueError(error):
        app.logger.error(error)
        return {"err": str(error)}, 400

    @app.errorhandler(400)
    def handle_BadRequest(error):
        app.logger.error(error)
        return {"err": str(error)}, 400

    @app.errorhandler(404)
    def handle_NotFound(error):
        app.logger.error(error)
        return {"err": str(error)}, 404

    @app.errorhandler(405)
    def handle_MethodNotAllowed(error):
        app.logger.error(error)
        return {"err": str(error)}, 405

    @app.errorhandler(415)
    def handle_UnsupportedMediaType(error):
        app.logger.error(error)
        return {"err": str(error)}, 415

    @app.errorhandler(HTTPException)
    def handle_HTTPException(error: HTTPException):
        app.logger.error(error)
        return {"err": str(error)}, error.code

    @app.errorhandler(Exception)
    def handle_Exception(error):
        app.logger.exception(error)
        return {"err": str(error)}, 500


def config_app(app: Flask, request: Request) -> None:
    _register_before_request(app, request)
    _register_errorhandlers(app)
