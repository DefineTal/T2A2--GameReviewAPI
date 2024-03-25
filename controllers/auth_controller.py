from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from init import db, bcrypt
from models.user import User, user_schema
from psycopg2 import errorcodes
from sqlalchemy.exc import IntegrityError


auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')


# Method=Post 
# Endpoint=/auth/register
# Creates new user
@auth_bp.route("/register", methods=["POST"]) 
def auth_register():
    try:
        # gets json input from body    
        body_data = user_schema.load(request.get_json())
        # creates user instance from input
        user = User(
            username = body_data.get('username'),
        )
        # password field from input stored here
        password = body_data.get('password')
        # checks if it exists
        if password:
            # encrypts
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        # error return if password input not found
        else:
            db.session.rollback()
            error = {"error": "password cant be null!"}
            return error, 409

        # commits the user instance to the database
        db.session.add(user)
        db.session.commit()
        # returns users newly created username
        return {"created new_user with username": body_data.get("username")}, 201

    # error catches for different types of errors
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Username is taken!"}, 409
        
    except ValidationError as val_err:
        return {"error": str(val_err)}, 400


# Method=Post 
# Endpoint=/auth/login
# Used for users to login using their credentials
@auth_bp.route("/login", methods=['POST'])
def auth_login():
    # convert body data to  python obj and search for matching username field
    body_data = request.get_json()
    stmt = db.Select(User).filter_by(username=body_data.get("username"))
    user = db.session.scalar(stmt)

    # check if details match else return error
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        #create jwt which expires after 24 hours
        jwt = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {"username": user.username, "jwt": jwt, "is_admin": user.is_admin}
    
    else:
        error = {"error": "email and password combination is incorrect"}
        return error, 401