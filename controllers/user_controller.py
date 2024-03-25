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


# Method=Get 
# Endpoint=/users
# Returns all user accounts
@users_bp.route('/')
def get_all_users():
    # selects all users and gets ready to order them
    stmt = db.select(User).order_by(User.id.asc())
    users = db.session.scalars(stmt)

    # returns selected users
    return users_schema.dump(users)


# Method=Get
# Endpoint=/users/<user_id>
# Returns single user account
@users_bp.route('/<int:user_id>')
def get_user(user_id):
    # finds user with matching id
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # if user exists return the user, else error
    if user:
        return user_schema.dump(user)
    else:
        return{"error": f"user id {user_id} doesn't exist. Please try again"}, 404


# Method=Delete
# Endpoint =/users/<user_id>
# Deletes a user account
@users_bp.route('/<int:user_id>', methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    # admin check for current user
    is_admin = is_user_admin()
    # finds user with matching id
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # if user exist -> check if user is current user or admin -> delete user if true else return error
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


# Method=Put,Patch
# Endpoint =/users/<user_id>
# Edits details of user account
@users_bp.route('/<int:user_id>', methods=["PUT", "PATCH"])
@jwt_required()
def edit_user(user_id):
    try:
        # admin check 
        is_admin = is_user_admin()
        # current user id check
        current_user_id = int(get_jwt_identity())
        # permission check
        if user_id == current_user_id or is_admin:
            # finds user with same id value as in url
            body_data = user_schema.load(request.get_json())
            stmt = db.select(User).filter_by(id = user_id)
            user = db.session.scalar(stmt)
            # if user exists compares input with user values
            if user:
                user.username = body_data.get("username") or user.username
                user.password = body_data.get("password") or user.password
                # commits changes to database
                db.session.commit()
                return user_schema.dump(user)       
            else:
                return {'error': f"user with id {user_id} not found"}, 404
        else:
            db.session.rollback()
            return {'error': f"Make sure your only editing an account that you are currently on or are authorised!"}, 403
        
    # error catches for different types of errors
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Username is taken!"}, 409
        
    except ValidationError as val_err:
        return {"error": str(val_err)}, 400


 # Function to find if current user is admin   
def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin





    
