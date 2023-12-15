from flask import Flask, Request
from werkzeug.exceptions import HTTPException


def register_errorhandlers(app: Flask, request: Request) -> Flask:
    @app.before_request
    def log_request_body():
        app.logger.info(request.get_data(as_text=True))

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

    @app.errorhandler(417)
    def handle_UnsupportedMediaType(error):
        app.logger.error(error)
        return {"err": str(error)}, 417

    @app.errorhandler(HTTPException)
    def handle_HTTPException(error):
        app.logger.error(error)
        return {"err": str(error)}, 400

    @app.errorhandler(Exception)
    def handle_Exception(error):
        app.logger.exception(error)
        return {"err": str(error)}, 500
