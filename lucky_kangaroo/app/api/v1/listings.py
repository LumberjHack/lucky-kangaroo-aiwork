from flask import Blueprint, jsonify

listings_bp = Blueprint('listings', __name__)

@listings_bp.get('/')
def list_listings():
    return jsonify({'listings': []})
