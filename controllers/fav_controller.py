from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db

from models.favourite import Favourite, favourite_schema, favourites_schema
from models.user import User

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes




fav_bp = Blueprint('favourites', __name__, url_prefix='<int:user_id>/favourites/')


# Method=Get
# Endpoint=<int:user_id>/favourites/
# Gets all favourites related to a user
@fav_bp.route('/')
def get_favs_for_user(user_id):
    # finds user with matching url id and returns all favourites related to user
    stmt = db.select(Favourite).filter_by(user_id = user_id)
    favourites = db.session.scalars(stmt)
    
    return favourites_schema.dump(favourites)


# Method=Post
# Endpoint=<int:user_id>/favourites/
# Creates a favourite for a user
@fav_bp.route('/', methods=["POST"])
@jwt_required()
def create_fav(user_id):
    try:
        # stores users current id as int rather than string
        current_user_id = int(get_jwt_identity())
        # checks if authorised
        if user_id == current_user_id:
            # gets input data
            body_data = request.get_json()
            # finds user id matching with url
            stmt = db.select(User).filter_by(id=user_id)
            user = db.session.scalar(stmt)
            # if user exists -> use input data and jwt token to create instance -> commit instance to database
            if user:
                fav = Favourite(
                    user_id = get_jwt_identity(),
                    game_id = body_data.get('game_id')
                )
                db.session.add(fav)
                db.session.commit()
                return favourite_schema.dump(fav)
            else:
                return {"error" f"User with id {user_id} doesnt exist!"}, 404
        else:
            return {"error": "Only make your own favourites!"}, 401
        
    except IntegrityError as err:
            if err.orig.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                return {"error": f"Could not find game with id of {fav.game_id}"}, 404
 
            
# Method=Delete
# Endpoint=<int:user_id>/favourites/<fav_id>
# Delete a favourite
@fav_bp.route('/<int:fav_id>', methods=["DELETE"])
@jwt_required()
def delete_fav(user_id, fav_id):
    # stores current user id as int
    current_user_id = int(get_jwt_identity())
    # checks if authorised -> if so find favourite with same id as url
    if user_id == current_user_id:
        stmt = db.select(Favourite).where(Favourite.id == fav_id)
        fav = db.session.scalar(stmt)
        # if fav exists deletes and commits to database
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return {'message': f"favourite with id {fav.id} deleted successfully"}
        else:
            db.session.rollback()
            return {'error': f"Favourite with id {fav_id} not found"}, 404
    else:
       return {"error": "Only delete your own favourites!"}, 401


@fav_bp.route('/<int:fav_id>', methods=["PUT", "PATCH"])
@jwt_required()
def edit_fav(user_id, fav_id):
    try:
        # stores current user id as int
        current_user_id = int(get_jwt_identity())
        # checks if authorised -> if so find favourite with same id as url
        if user_id == current_user_id:
            body_data = request.get_json()
            stmt = db.select(Favourite).where(Favourite.id == fav_id)
            fav = db.session.scalar(stmt)
            # if exists use current user id and input body and compare with existing instance
            if fav:
                fav.user_id = get_jwt_identity()
                fav.game_id = body_data.get('game_id') or fav.game_id
                db.session.commit()
                return favourite_schema.dump(fav)       
            else:
                return {'error': f"Favourite with id {fav_id} not found"}, 404
        else:
            return {"error": "Only edit your own favourites!"}, 401
    
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
            db.session.rollback()
            return {"error": "Could not find game"}, 404

    