from flask import Blueprint, request
from init import db, bcrypt
from models.user import User, user_schema
from psycopg2 import errorcodes
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from datetime import timedelta 
from marshmallow import ValidationError


auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')

@auth_bp.route("/register", methods=["POST"]) # /auth/register
def auth_register():
    try:    
        body_data = user_schema.load(request.get_json())
        
        user = User(
            username = body_data.get('username'),
        )

        password = body_data.get('password')

        if password:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')

        else:
            error = {"error": "password cant be null!"}
            return error, 409

        db.session.add(user)
        db.session.commit()

        return {"created new_user with username": body_data.get("username")}, 201


    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Username is taken!"}, 409
        
    except ValidationError as val_err:
        return {"error": str(val_err)}, 400



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