from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.favourite import Favourite, favourite_schema, favourites_schema

fav_bp = Blueprint('favourites', __name__, url_prefix='/favourites/')

@fav_bp.route('/')
def get_all_favs():
    stmt = db.select(Favourite).order_by(Favourite.id.asc())
    favourites = db.session.scalars(stmt)
    return favourites_schema.dump(favourites)

@fav_bp.route('/<int:favourite_id>')
def get_dev(favourite_id):
    stmt = db.select(Favourite).filter_by(id=favourite_id)
    developer = db.session.scalar(stmt)
    if developer:
        return favourite_schema.dump(developer)
    else:
        return{"error": f"user id {favourite_id} doesn't exist. Please try again"}, 404