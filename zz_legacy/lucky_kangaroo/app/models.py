import uuid as _uuid
from datetime import datetime
from .extensions import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(_uuid.uuid4()), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(BaseModel):
    __tablename__ = 'users'
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    def to_dict(self):
        data = super().to_dict()
        # Security: remove sensitive fields
        data.pop('password_hash', None)
        return data


class Listing(BaseModel):
    __tablename__ = 'listings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)


class Image(BaseModel):
    __tablename__ = 'images'
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(64))
