from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        response = e.get_response()
        response.data = jsonify({
            'success': False,
            'error': e.name,
            'message': e.description,
            'code': e.code,
        }).data
        response.content_type = 'application/json'
        return response

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Not Found', 'message': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'success': False, 'error': 'Server Error', 'message': 'Internal server error'}), 500
