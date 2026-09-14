"""
SQLAlchemy models for Pendakian Lawu Savings Website.

Tables
------
users           – admin + participant accounts
savings         – every savings record submitted by a user
climbing_info   – general climb event information
route_items     – individual itinerary / route entries linked to a climbing_info
"""

from datetime import datetime
from .database import db


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(120), nullable=False)
    role          = db.Column(db.String(10), nullable=False, default='user')  # 'admin' | 'user'
    is_active     = db.Column(db.Boolean, default=True, nullable=False)

    # savings-specific fields (null for admin)
    target_amount = db.Column(db.Float, nullable=True)
    phone_number  = db.Column(db.String(20), nullable=True)
    notes         = db.Column(db.Text, nullable=True)

    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    savings = db.relationship('Savings', backref='participant', lazy=True,
                              foreign_keys='Savings.user_id')

    # ------------------------------------------------------------------ helpers
    @property
    def total_verified(self):
        return sum(s.amount for s in self.savings if s.status == 'verified')

    @property
    def shortfall(self):
        if self.target_amount:
            diff = self.target_amount - self.total_verified
            return max(diff, 0)
        return None

    @property
    def progress_percent(self):
        if self.target_amount and self.target_amount > 0:
            pct = (self.total_verified / self.target_amount) * 100
            return min(round(pct, 1), 100)
        return 0

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Savings(db.Model):
    __tablename__ = 'savings'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status      = db.Column(db.String(10), nullable=False, default='pending')
                  # 'pending' | 'verified' | 'rejected'
    rejection_note = db.Column(db.Text, nullable=True)

    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationship back to the admin who verified
    verifier = db.relationship('User', foreign_keys=[verified_by])

    def __repr__(self):
        return f'<Savings id={self.id} user={self.user_id} amount={self.amount} status={self.status}>'


class ClimbingInfo(db.Model):
    __tablename__ = 'climbing_info'

    id              = db.Column(db.Integer, primary_key=True)
    mountain_name   = db.Column(db.String(100), nullable=False)
    climb_date      = db.Column(db.String(50), nullable=True)   # stored as string for flexibility
    meeting_point   = db.Column(db.String(200), nullable=True)
    description     = db.Column(db.Text, nullable=True)
    equipment_notes = db.Column(db.Text, nullable=True)
    important_notes = db.Column(db.Text, nullable=True)
    is_active       = db.Column(db.Boolean, default=True)       # which event is currently shown

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationship
    route_items = db.relationship('RouteItem', backref='climbing_event', lazy=True,
                                  order_by='RouteItem.order_index',
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ClimbingInfo {self.mountain_name}>'


class RouteItem(db.Model):
    __tablename__ = 'route_items'

    id               = db.Column(db.Integer, primary_key=True)
    climbing_info_id = db.Column(db.Integer, db.ForeignKey('climbing_info.id'), nullable=False)
    order_index      = db.Column(db.Integer, default=0)
    item_type        = db.Column(db.String(20), nullable=False, default='checkpoint')
                       # 'checkpoint' | 'note' | 'image' | 'map_link'
    title            = db.Column(db.String(150), nullable=False)
    content          = db.Column(db.Text, nullable=True)   # description / URL / map link
    elevation        = db.Column(db.String(30), nullable=True)  # e.g. "2.900 mdpl"
    duration         = db.Column(db.String(50), nullable=True)  # e.g. "± 2 jam"

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RouteItem {self.title}>'
