from app import db
from datetime import datetime
from decimal import Decimal

class Payment(db.Model):
    """Model for storing payment information"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)
    payment_intent_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    payment_metadata = db.Column(db.JSON)
    refunded_amount = db.Column(db.Numeric(10, 2))
    refunded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref=db.backref('payments', lazy=True))
    history = db.relationship('PaymentHistory', backref='payment', lazy=True)
    disputes = db.relationship('PaymentDispute', backref='payment', lazy=True)
    
    def __init__(self, order_id, amount, currency, payment_method, payment_intent_id, status, metadata=None):
        self.order_id = order_id
        self.amount = amount
        self.currency = currency
        self.payment_method = payment_method
        self.payment_intent_id = payment_intent_id
        self.status = status
        self.payment_metadata = metadata
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_intent_id': self.payment_intent_id,
            'status': self.status,
            'metadata': self.payment_metadata,
            'refunded_amount': float(self.refunded_amount) if self.refunded_amount else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Payment {self.id}>'

class PaymentHistory(db.Model):
    """Model for storing payment history"""
    __tablename__ = 'payment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # payment, refund, etc.
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, payment_id, status, type, details=None):
        self.payment_id = payment_id
        self.status = status
        self.type = type
        self.details = details
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'status': self.status,
            'type': self.type,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PaymentHistory {self.id}>'

class PaymentDispute(db.Model):
    """Model for storing payment disputes"""
    __tablename__ = 'payment_disputes'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    dispute_id = db.Column(db.String(100), unique=True, nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    evidence = db.Column(db.JSON)
    status = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    resolution = db.Column(db.Text)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resolver = db.relationship('User', backref=db.backref('resolved_disputes', lazy=True))
    
    def __init__(self, payment_id, dispute_id, reason, evidence, status, amount):
        self.payment_id = payment_id
        self.dispute_id = dispute_id
        self.reason = reason
        self.evidence = evidence
        self.status = status
        self.amount = amount
    
    def resolve(self, resolution, resolved_by):
        """Resolve a dispute"""
        self.resolution = resolution
        self.resolved_by = resolved_by
        self.resolved_at = datetime.utcnow()
        self.status = 'resolved'
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'dispute_id': self.dispute_id,
            'reason': self.reason,
            'evidence': self.evidence,
            'status': self.status,
            'amount': float(self.amount),
            'resolution': self.resolution,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PaymentDispute {self.id}>' 