from flask import Blueprint, request
from init import db, bcrypt
from models.user import User, user_schema
from psycopg2 import errorcodes
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')

@auth_bp.route("/register", methods=["POST"]) # /auth/register
def auth_register():
    try:    
        body_data = request.get_json()
        hashed_password = ""
        password = body_data.get('password')
        
        # checks if password field is null
        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # if null returns error
        else:
            error = {"error": "password cant be null!"}
            return error, 409
        

        user = User(
            username = body_data.get('username'),
            password = hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201


    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Username is taken!"}, 409
    