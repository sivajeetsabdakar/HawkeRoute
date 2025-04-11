from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app import db
from datetime import datetime, timedelta
import jwt
from app.services.notification import NotificationService

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'phone', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate role
    if data['role'] not in ['customer', 'hawker']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone number already registered'}), 409
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        password=data['password'],
        role=data['role']
    )
    
    # Add hawker-specific fields if role is hawker
    if data['role'] == 'hawker':
        if not all(field in data for field in ['business_name', 'business_address']):
            return jsonify({'error': 'Missing hawker-specific fields'}), 400
        
        user.business_name = data['business_name']
        user.business_address = data['business_address']
        user.latitude = data.get('latitude')
        user.longitude = data.get('longitude')
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(field in data for field in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    user_id = get_jwt_identity()
    expires_at = datetime.fromtimestamp(get_jwt()["exp"])

    blacklisted_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )

    db.session.add(blacklisted_token)
    db.session.commit()

    return jsonify({"message": "Successfully logged out"}), 200

@bp.route('/password-reset-request', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Return success even if user doesn't exist to prevent email enumeration
        return jsonify({"message": "If your email is registered, you will receive a password reset link"}), 200

    # Generate password reset token
    reset_token = create_access_token(
        identity=user.id,
        additional_claims={"type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )

    # Send password reset email
    NotificationService.send_system_notification(
        user_id=user.id,
        notification_type="password_reset",
        data={"reset_token": reset_token}
    )

    return jsonify({"message": "If your email is registered, you will receive a password reset link"}), 200

@bp.route('/password-reset', methods=['POST'])
@jwt_required()
def password_reset():
    # Verify token type
    if get_jwt()["type"] != "password_reset":
        return jsonify({"error": "Invalid token type"}), 400

    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
    user.set_password(new_password)
    db.session.commit()

    # Blacklist the reset token
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    expires_at = datetime.fromtimestamp(get_jwt()["exp"])

    blacklisted_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )

    db.session.add(blacklisted_token)
    db.session.commit()

    return jsonify({"message": "Password successfully reset"}), 200

@bp.route('/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    # Verify token type
    if get_jwt()["type"] != "email_verification":
        return jsonify({"error": "Invalid token type"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update email verification status
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    db.session.commit()

    # Blacklist the verification token
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    expires_at = datetime.fromtimestamp(get_jwt()["exp"])

    blacklisted_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )

    db.session.add(blacklisted_token)
    db.session.commit()

    return jsonify({"message": "Email successfully verified"}), 200

@bp.route('/resend-verification', methods=['POST'])
@jwt_required()
def resend_verification():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.email_verified:
        return jsonify({"error": "Email already verified"}), 400

    # Generate email verification token
    verification_token = create_access_token(
        identity=user.id,
        additional_claims={"type": "email_verification"},
        expires_delta=timedelta(hours=24)
    )

    # Send verification email
    NotificationService.send_system_notification(
        user_id=user.id,
        notification_type="email_verification",
        data={"verification_token": verification_token}
    )

    return jsonify({"message": "Verification email sent"}), 200 