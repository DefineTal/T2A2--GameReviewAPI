
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db

from models.game import Game, game_schema, games_schema

from controllers.review_controller import review_bp
from controllers.user_controller import is_user_admin

from sqlalchemy.exc import IntegrityError, ArgumentError
from psycopg2 import errorcodes

game_bp = Blueprint('games', __name__, url_prefix='/games/')
game_bp.register_blueprint(review_bp)


# Method=Get
# Endpoint=/games
# Gets all games
@game_bp.route('/')
def get_all_games():
    # stores all games in ascending order
    stmt = db.select(Game).order_by(Game.id.asc())
    games = db.session.scalars(stmt)
    # returns all games
    return games_schema.dump(games)


# Method=Get
# Endpoint=/games/<game_id>
# Gets a game
@game_bp.route('/<int:game_id>')
def get_game(game_id):
    # find game with id matching url
    stmt = db.select(Game).filter_by(id=game_id)
    game = db.session.scalar(stmt)
    # if exists -> return game, else return error
    if game:
        return game_schema.dump(game)
    else:
        return{"error": f"user id {game_id} doesn't exist. Please try again"}, 404


# Method=Post
# Endpoint=/games/<game_id>
# Creates a game
@game_bp.route('/', methods=["POST"])
@jwt_required()
def create_game():
    # store input data
    body_data = request.get_json()
    # create game instance based on input data -> add & commit instance to database
    try:      
        game = Game(
            title = body_data.get('title'),
            description = body_data.get('description'),
            genre = body_data.get('genre'),
            publisher = body_data.get('publisher'),
            release_date = body_data.get('release_date'),
            developer_id = body_data.get('developer_id')
        )
        db.session.add(game)
    
    except AttributeError:
        return {"error": "Attribute error! Double check the json input fields!"}, 400

    try:
        db.session.commit()
        return game_schema.dump(game)
  
    # error catches for different types of errors
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Game name already recorded!"}, 409
        
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid date try again!"}, 409
        
        return {"error": "An integrity error occurred"}, 500
    
    except:
        return {"error": "Data error. Try again!"}, 409



# Method=Delete
# Endpoint=/games/<game_id>
# Deletes a game 
@game_bp.route('/<int:game_id>', methods = ["DELETE"])
@jwt_required()
def delete_game(game_id):
    # check if user admin
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "You are not authorized to delete games"}
    # finds game with same id as in url
    stmt = db.select(Game).where(Game.id == game_id)
    game = db.session.scalar(stmt)
    # if exists -> delete and commit, else return error
    if game:
        db.session.delete(game)
        db.session.commit()
        return {'message': f"dev {game.title} deleted successfully"}
    else:
        db.session.rollback()
        return {'error': f"game with id {game_id} not found"}, 404


# Method=Put,Patch
# Endpoint=/games/<game_id>
# Edits a game
@game_bp.route('/<int:game_id>', methods = ["PUT", "PATCH"])
@jwt_required()
def update_game(game_id):
    try:
        # stores data from body input
        body_data = request.get_json()
        # finds game with matching id as in url
        stmt = db.select(Game).filter_by(id = game_id)
        game = db.session.scalar(stmt)
        # if exists -> compare new data with old -> update fields and commit to database, else return error
        if game:
            game.title = body_data.get('title') or game.title
            game.description = body_data.get('description') or game.description
            game.genre = body_data.get('genre') or game.genre
            game.publisher = body_data.get('publisher') or game.publisher
            game.release_date = body_data.get('release_date') or game.release_date
            game.developer_id = body_data.get('developer_id') or game.developer_id
            db.session.commit()
            return game_schema.dump(game)
        else:
            return{'error': f"game with id {game_id} not found"}, 404
        
    # error catches for different types of errors
    except IntegrityError as err:
        db.session.rollback()

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Game name already recorded!"}, 409
        
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid date try again!"}, 409