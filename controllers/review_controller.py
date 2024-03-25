from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db

from models.game import Game

from models.review import Review, review_schema, reviews_schema

from sqlalchemy.exc import IntegrityError, StatementError
from psycopg2 import errorcodes

review_bp = Blueprint('reviews', __name__, url_prefix='<int:game_id>/reviews/')


# Method=Get
# Endpoint=<int:game_id>/reviews/
# Gets all reviews for a game
@review_bp.route('/')
def get_all_reviews(game_id):
    # finds all reviews with game id matching url
    stmt = db.select(Review).filter_by(game_id = game_id)
    reviews = db.session.scalars(stmt)
    # returns them to user
    return reviews_schema.dump(reviews)


# Method=Post
# Endpoint=<int:game_id>/reviews/
# Create review for a game
@review_bp.route('/', methods=["POST"])
@jwt_required()
def create_review(game_id):
    # stores data from input
    body_data = request.get_json()
    # finds game with id matching url
    stmt = db.select(Game).filter_by(id=game_id)
    game = db.session.scalar(stmt)
    # if game exists -> uses input to create a review instance -> adds and commits to database, else return error
    if game:
        review = Review(
            user_id = get_jwt_identity(),
            game_id = game.id,
            rating = body_data.get('rating'),
            date_made = body_data.get('date_made' ),
            completed = body_data.get('completed'),
            content = body_data.get('content')
        )

        db.session.add(review)
        db.session.commit()
        return review_schema.dump(review)
    else:
        return {"error" f"game with id {game_id} doesnt exist!"}, 404
    
    
# Method=Delete
# Endpoint=<int:game_id>/reviews/<review_id>
# Delete review for a game
@review_bp.route('/<int:review_id>', methods=["DELETE"])
@jwt_required()
def delete_review(review_id, game_id):
    try:
        # stores current user id as int
        current_user_id = int(get_jwt_identity())
        # finds Review with id matching url
        stmt = db.select(Review).filter_by(id=review_id)
        review = db.session.scalar(stmt)
        # checks if authorised -> deletes and commits if true
        if review.user.id == current_user_id:
            if review and review.game.id == game_id:
                db.session.delete(review)
                db.session.commit()
                return{"message": f"Review with id {review_id} has been deleted"}
            else:
                return{"error": f"Review with id {review_id} not found in game with id {game_id}"}, 404
        else:
            return {"error": "You are not authorised to delete this review"}, 401
        
    except AttributeError:
        return {"error": f"Review with id of {review_id} doesnt exist"}, 404
    

# Method=Put,Patch
# Endpoint=<int:game_id>/reviews/<review_id>
# Edit review for a game
@review_bp.route('/<int:review_id>', methods=["PUT", "PATCH"])
@jwt_required()
def edit_review(review_id, game_id):
    try:
        # stores current user id as int
        current_user_id = int(get_jwt_identity())
        # stores data from input
        body_data = request.get_json()
        # finds review with matching id and game id from url
        stmt = db.select(Review).filter_by(id=review_id, game_id=game_id)
        review = db.session.scalar(stmt)
        # if authorised -> compares old review with new review and updates changed fields -> commit changes to database, else return error
        if review.user.id == current_user_id:
            if review:
                review.rating = body_data.get('rating') or review.rating

                review.completed = body_data.get('completed') or review.completed
                review.content = body_data.get('content') or review.content

                db.session.commit()
                return review_schema.dump(review)
            else:
                return {"error": f"Review with id {review_id} not found in game with id {game_id}"}, 404
        else:
            return {"error": "You are not authorised to edit this review"}, 401
    # error catches for different types of errors    
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid rating try again! 1-10 are valid inputs"}, 409

    except StatementError as state:
        return {"error": "'completed' column must be a boolean value!"}, 409