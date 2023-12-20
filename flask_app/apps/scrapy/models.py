from datetime import datetime
from apps.app import db


class UserKeyword(db.Model):
    __tablename__ = 'user_keywords'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    is_scraped = db.Column(db.Boolean, default=False)
    keyword = db.Column(db.String(255))
    year1 = db.Column(db.String(4))
    year2 = db.Column(db.String(4)) 
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    