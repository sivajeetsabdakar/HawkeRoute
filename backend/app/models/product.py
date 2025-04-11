from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    hawker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hawker = db.relationship('User', backref=db.backref('products', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'hawker_id': self.hawker_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'hawker_name': self.hawker.business_name or self.hawker.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 