from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.review import Review, review_schema, reviews_schema

review_bp = Blueprint('reviews', __name__, url_prefix='<int:game_id>/reviews/')


@review_bp.route('/')
def get_all_reviews(game_id):
    stmt = db.select(Review).filter_by(game_id = game_id)
    reviews = db.session.scalars(stmt)
    
    return reviews_schema.dump(reviews)
