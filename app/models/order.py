from app import db
from datetime import datetime

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    # Relationships
    product = db.relationship('Product')

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hawker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, preparing, delivering, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.String(200), nullable=False)
    delivery_latitude = db.Column(db.Float, nullable=False)
    delivery_longitude = db.Column(db.Float, nullable=False)
    delivery_instructions = db.Column(db.Text)
    delivery_time = db.Column(db.DateTime)  # Estimated or actual delivery time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Payment related fields
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded, partially_refunded
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    
    # Cancellation related fields
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cancellation_reason = db.Column(db.String(200), nullable=True)
    cancellation_details = db.Column(db.Text, nullable=True)
    refund_status = db.Column(db.String(20), nullable=True)  # pending, completed, failed
    refund_amount = db.Column(db.Float, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_orders', lazy=True))
    hawker = db.relationship('User', foreign_keys=[hawker_id], backref=db.backref('hawker_orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    canceller = db.relationship('User', foreign_keys=[cancelled_by], backref=db.backref('cancelled_orders', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'hawker_id': self.hawker_id,
            'status': self.status,
            'total_amount': self.total_amount,
            'delivery_address': self.delivery_address,
            'delivery_latitude': self.delivery_latitude,
            'delivery_longitude': self.delivery_longitude,
            'delivery_instructions': self.delivery_instructions,
            'delivery_time': self.delivery_time.isoformat() if self.delivery_time else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'payment_status': self.payment_status,
            'payment_id': self.payment_id,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancelled_by': self.cancelled_by,
            'cancellation_reason': self.cancellation_reason,
            'cancellation_details': self.cancellation_details,
            'refund_status': self.refund_status,
            'refund_amount': self.refund_amount,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price
                } for item in self.items
            ],
            'customer_name': self.customer.name,
            'hawker_name': self.hawker.business_name or self.hawker.name
        } 

class OrderRating(db.Model):
    """Model for storing order ratings"""
    
    __tablename__ = 'order_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    
    # Generic rating categories applicable to all products
    product_quality = db.Column(db.Integer)  # 1-5 stars
    delivery_time = db.Column(db.Integer)  # 1-5 stars
    communication = db.Column(db.Integer)  # 1-5 stars
    packaging = db.Column(db.Integer)  # 1-5 stars
    value_for_money = db.Column(db.Integer)  # 1-5 stars
    product_condition = db.Column(db.Integer)  # 1-5 stars (for physical products)
    
    # Additional feedback
    tags = db.Column(db.JSON)  # e.g., ["high_quality", "fast_delivery", "friendly"]
    photos = db.Column(db.JSON)  # URLs to photos uploaded with rating
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref=db.backref('rating', uselist=False))
    user = db.relationship('User', backref='ratings')
    
    def __init__(self, order_id, user_id, rating, comment=None, 
                 product_quality=None, delivery_time=None, communication=None,
                 packaging=None, value_for_money=None, product_condition=None,
                 tags=None, photos=None):
        self.order_id = order_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
        self.product_quality = product_quality
        self.delivery_time = delivery_time
        self.communication = communication
        self.packaging = packaging
        self.value_for_money = value_for_money
        self.product_condition = product_condition
        self.tags = tags or []
        self.photos = photos or []
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'product_quality': self.product_quality,
            'delivery_time': self.delivery_time,
            'communication': self.communication,
            'packaging': self.packaging,
            'value_for_money': self.value_for_money,
            'product_condition': self.product_condition,
            'tags': self.tags,
            'photos': self.photos,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrderRating {self.id}: {self.rating} stars>'

class OrderDispute(db.Model):
    """Model for storing order disputes"""
    
    __tablename__ = 'order_disputes'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.JSON)  # Links to evidence files
    status = db.Column(db.String(20), nullable=False)  # pending, resolved, rejected
    resolution = db.Column(db.JSON)  # Resolution details
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref=db.backref('disputes', lazy=True))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('disputes_created', lazy=True))
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref=db.backref('disputes_resolved', lazy=True))
    
    def __init__(self, order_id, user_id, reason, description, evidence=None, status='pending'):
        self.order_id = order_id
        self.user_id = user_id
        self.reason = reason
        self.description = description
        self.evidence = evidence
        self.status = status
    
    def to_dict(self):
        """Convert dispute to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'reason': self.reason,
            'description': self.description,
            'evidence': self.evidence,
            'status': self.status,
            'resolution': self.resolution,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<OrderDispute {self.id}: {self.status}>'

class CancellationReason(db.Model):
    """Model for storing standardized cancellation reasons"""
    
    __tablename__ = 'cancellation_reasons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # customer, hawker, system, etc.
    requires_refund = db.Column(db.Boolean, default=True)
    refund_percentage = db.Column(db.Float, default=100.0)  # Percentage of order amount to refund
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, code, name, description=None, category='customer', 
                 requires_refund=True, refund_percentage=100.0):
        self.code = code
        self.name = name
        self.description = description
        self.category = category
        self.requires_refund = requires_refund
        self.refund_percentage = refund_percentage
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'requires_refund': self.requires_refund,
            'refund_percentage': self.refund_percentage,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CancellationReason {self.code}: {self.name}>' 