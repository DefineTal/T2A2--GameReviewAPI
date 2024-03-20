from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.review import Review, review_schema, reviews_schema

review_bp = Blueprint('reviews', __name__, url_prefix='/reviews/')

@review_bp.route('/')
def get_all_reviews():
    stmt = db.select(Review).order_by(Review.id.asc())
    favourites = db.session.scalars(stmt)
    return reviews_schema.dump(favourites)

@review_bp.route('/<int:review_id>')
def get_review(review_id):
    stmt = db.select(Review).filter_by(id=review_id)
    review = db.session.scalar(stmt)
    if review:
        return review_schema.dump(review)
    else:
        return{"error": f"user id {review_id} doesn't exist. Please try again"}, 404
