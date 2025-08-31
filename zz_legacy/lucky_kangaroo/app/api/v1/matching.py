from flask import Blueprint, jsonify

matching_bp = Blueprint('matching', __name__)

@matching_bp.get('/recommendations')
def recommendations():
    return jsonify({'recommendations': []})
