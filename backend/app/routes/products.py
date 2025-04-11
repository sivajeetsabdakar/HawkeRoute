from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.product import Product
from app.models.user import User
from app import db
from datetime import datetime

bp = Blueprint('products', __name__)

@bp.route('', methods=['GET'])
def get_products():
    # Get query parameters
    hawker_id = request.args.get('hawker_id', type=int)
    is_available = request.args.get('is_available', type=bool)
    
    # Base query
    query = Product.query
    
    # Apply filters
    if hawker_id:
        query = query.filter_by(hawker_id=hawker_id)
    if is_available is not None:
        query = query.filter_by(is_available=is_available)
    
    # Get products
    products = query.order_by(Product.created_at.desc()).all()
    return jsonify([product.to_dict() for product in products]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'hawker':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        product = Product(
            hawker_id=current_user_id,
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product.to_dict()), 200

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'hawker':
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.hawker_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'is_available' in data:
            product.is_available = data['is_available']
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'hawker':
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.hawker_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 