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
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_orders', lazy=True))
    hawker = db.relationship('User', foreign_keys=[hawker_id], backref=db.backref('hawker_orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
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
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref=db.backref('ratings', lazy=True))
    user = db.relationship('User', backref=db.backref('order_ratings', lazy=True))
    
    def __init__(self, order_id, user_id, rating, comment=None):
        self.order_id = order_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
    
    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
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