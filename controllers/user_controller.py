from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.user import User, users_schema, user_schema


users_bp = Blueprint('users', __name__, url_prefix='/users/')


@users_bp.route('/')
def get_all_users():
    stmt = db.select(User).order_by(User.id.asc())
    users = db.session.scalars(stmt)
    return users_schema.dump(users)

@users_bp.route('/<int:user_id>')
def get_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if user:
        return user_schema.dump(user)
    else:
        return{"error": f"Card id {user_id} doesnt exist. Please try again"}, 404