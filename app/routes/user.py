from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.user import UserService
from app.middleware.validation import validate_request
from app.schemas.user import UserUpdateSchema

bp = Blueprint('user', __name__)

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the current user's profile"""
    try:
        user_id = get_jwt_identity()
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
@validate_request(UserUpdateSchema)
def update_profile():
    """Update the current user's profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        updated_user = UserService.update_user(user_id, data)
        return jsonify(updated_user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get the current user's notification preferences"""
    try:
        user_id = get_jwt_identity()
        preferences = UserService.get_user_preferences(user_id)
        return jsonify(preferences), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update the current user's notification preferences"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        updated_preferences = UserService.update_user_preferences(user_id, data)
        return jsonify(updated_preferences), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    """Get the current user's order history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        orders = UserService.get_user_orders(user_id, page, per_page)
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 