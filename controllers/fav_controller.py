from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.favourite import Favourite, favourite_schema, favourites_schema

fav_bp = Blueprint('favourites', __name__, url_prefix='<int:user_id>/favourites/')

@fav_bp.route('/')
def get_all_favs(user_id):
    stmt = db.select(Favourite).filter_by(user_id = user_id)
    favourites = db.session.scalars(stmt)
    
    return favourites_schema.dump(favourites)
