from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.user import User, users_schema


users_bp = Blueprint('users', __name__, url_prefix='/users/')


@users_bp.route('/')
def get_all_users():
    stmt = db.select(User).order_by(User.id.asc())
    users = db.session.scalars(stmt)
    return users_schema.dump(users)