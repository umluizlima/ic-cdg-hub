"""
Data model for users.

Every user has a firstname, lastname, email and password.
A user might be admin.
"""

import os
import re
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.model import db
import app.controller.utils as utils


definition = {
    'types': {
        'first_name': [str],
        'last_name': [str],
        'email': [str],
        'password': [str],
        'confirm': [str],
        'admin': [bool],
        'token': [str, type(None)]
    },
    'required': ['first_name', 'last_name', 'email', 'password', 'confirm'],
    'unique': ['email', 'token']
}


class User(db.Model):
    """Data model for users."""

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    token = db.Column(db.Text, unique=True)
    token_exp = db.Column(db.DateTime)
    reservations = db.relationship('Reservation',
                                   backref='user',
                                   lazy=True)
    lendings = db.relationship('Lending',
                               backref='user',
                               lazy=True)

    def set_password(self, password):
        """Set user password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if user password matches given password."""
        return check_password_hash(self.password, password)

    def get_token(self, expires_in=3600):
        """Get user's token, or generates a new one."""
        now = datetime.utcnow()
        # Return current token if still valid
        if self.token and self.token_exp \
                and self.token_exp > now + timedelta(seconds=60):
            return self.token
        # Generate a new token
        payload = {
            'user_id': self.id,
            'admin': self.admin
        }
        self.token = jwt.encode(payload,
                                os.environ.get('SECRET_KEY') or 'secret')
        self.token_exp = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token.decode('UTF-8')

    def revoke_token(self):
        """Instantly revokes user's current token."""
        self.token_exp = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """Return user whom token belongs to."""
        print(token)
        try:
            payload = jwt.decode(
                token,
                os.environ.get('SECRET_KEY') or 'secret'
            )
        except Exception:
            return None
        print(payload)
        user = User.query.filter_by(id=payload['user_id']).first()
        print(user)
        print(user.to_dict())
        print(user.password)
        print(user.token_exp)
        # if user is None or user.token_exp is None \
        #         or user.token_exp < datetime.utcnow():
        #     return None
        if user is None:
            return None
        print('validou o token')
        return user

    def to_dict(self):
        """Return a User object formatted as dict."""
        obj = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "admin": self.admin
        }
        return obj

    def from_dict(self, data, new_user=False):
        """Fill User attributes from given dictionary."""
        for field in ['first_name', 'last_name', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if 'admin' in data and bool(data['admin']) is True:
            setattr(self, 'admin', True)
        if new_user and 'password' in data:
            self.set_password(data['password'])

    @staticmethod
    def check_data(data: dict, new: bool = False):
        error = utils.check_data(data, definition, new) \
            or utils.check_name(data, 'first_name') \
            or utils.check_name(data, 'last_name') \
            or utils.check_email(data, 'email')
        if new:
            if 'password' in data and 'confirm' in data:
                if data['password'] != data['confirm']:
                    return 'password e confirm devem ser iguais'

        return error
