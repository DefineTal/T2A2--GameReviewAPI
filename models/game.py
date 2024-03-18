from init import db, ma
from sqlalchemy import CheckConstraint, func
from marshmallow import fields
from datetime import datetime


class Game(db.Model):
    __tablename__ = "games"

    # Model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(20))
    publisher = db.Column(db.String(25))
    release_date = db.Column(db.Date, nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developers.id'), nullable=False)
    
    # CheckConstraint to ensure release_date is in the past
    __table_args__ = (
        CheckConstraint('release_date < CURRENT_DATE', name='check_future'),
    )

class GameSchema(ma.Schema):

    developer = fields.Nested('DeveloperSchema', only = ['name'])

    class Meta:
        fields = ('id', 'title', 'description', 'genre', 'publisher', 'release_date', 'developer')


game_schema = GameSchema()
games_schema = GameSchema(many = True)