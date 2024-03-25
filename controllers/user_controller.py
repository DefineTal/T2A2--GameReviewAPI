from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db, bcrypt

from models.user import User, users_schema, user_schema

from controllers.fav_controller import fav_bp

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from marshmallow import ValidationError

users_bp = Blueprint('users', __name__, url_prefix='/users/')
users_bp.register_blueprint(fav_bp)


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
        return{"error": f"user id {user_id} doesn't exist. Please try again"}, 404


@users_bp.route('/<int:user_id>', methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    is_admin = is_user_admin()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if user:
        if user_id == get_jwt_identity or is_admin:
            db.session.delete(user)
            db.session.commit()
            return {'message': f"user with id of {user.id} and username of {user.username} deleted successfully"}
        else:
            db.session.rollback()
            return {'error': f"Make sure your only deleting an account that you are currently on or are authorised!"}, 403
    else:
        db.session.rollback()
        return {"error": f"user id {user_id} doesn't exist. Please try again"}, 404


@users_bp.route('/<int:user_id>', methods=["PUT", "PATCH"])
@jwt_required()
def edit_user(user_id):
    try:
        is_admin = is_user_admin()
        current_user_id = int(get_jwt_identity())
        if user_id == current_user_id or is_admin:
            body_data = user_schema.load(request.get_json())
            stmt = db.select(User).filter_by(id = user_id)
            user = db.session.scalar(stmt)
            if user:
                user.username = body_data.get("username") or user.username
                user.password = body_data.get("password") or user.password

                db.session.commit()
                return user_schema.dump(user)       
            else:
                return {'error': f"user with id {user_id} not found"}, 404
        else:
            db.session.rollback()
            return {'error': f"Make sure your only editing an account that you are currently on or are authorised!"}, 403
    
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Username is taken!"}, 409
        
    except ValidationError as val_err:
        return {"error": str(val_err)}, 400

    
def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin





    
