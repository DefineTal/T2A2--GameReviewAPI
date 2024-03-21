from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.game import Game, game_schema, games_schema
from psycopg2 import errorcodes
from sqlalchemy.exc import IntegrityError, ArgumentError

game_bp = Blueprint('games', __name__, url_prefix='/games/')

@game_bp.route('/')
def get_all_games():
    stmt = db.select(Game).order_by(Game.id.asc())
    games = db.session.scalars(stmt)
    return games_schema.dump(games)


@game_bp.route('/<int:game_id>')
def get_game(game_id):
    stmt = db.select(Game).filter_by(id=game_id)
    game = db.session.scalar(stmt)
    if game:
        return game_schema.dump(game)
    else:
        return{"error": f"user id {game_id} doesn't exist. Please try again"}, 404
    
@game_bp.route('/', methods=["POST"])
#@jwt_required()
def create_dev():
    body_data = request.get_json()
    game = Game(
        title = body_data.get('title'),
        description = body_data.get("description"),
        genre = body_data.get("genre"),
        publisher = body_data.get("publisher"),
        release_date = body_data.get("release_date"),
        developer = body_data.get("developer")
    )
    db.session.add(game)

    try:
        db.session.commit()
        return game_schema.dump(game)
  
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