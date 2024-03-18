from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.game import Game, game_schema, games_schema

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