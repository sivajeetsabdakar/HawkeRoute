from app import db
from datetime import datetime

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti, token_type, user_id, expires_at):
        self.jti = jti
        self.token_type = token_type
        self.user_id = user_id
        self.expires_at = expires_at

    @classmethod
    def is_blacklisted(cls, jti):
        return cls.query.filter_by(jti=jti).first() is not None 