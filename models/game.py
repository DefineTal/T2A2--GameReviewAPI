from init import db, ma
from sqlalchemy import CheckConstraint
from marshmallow import fields
from marshmallow.validate import Length
from datetime import datetime


class Game(db.Model):
    __tablename__ = "games"

    # Model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique = True)
    description = db.Column(db.Text)
    genre = db.Column(db.String(20))
    publisher = db.Column(db.String(25))
    release_date = db.Column(db.Date, nullable=False)

    developer_id = db.Column(db.Integer, db.ForeignKey('developers.id'), nullable=False)

    developer = db.relationship('Developer', back_populates = 'games')
    favourites = db.relationship('Favourite', back_populates = 'game', cascade = 'all, delete')
    reviews = db.relationship('Review', back_populates = 'game', cascade = 'all, delete')
    
    # CheckConstraint to ensure release_date is in the past
    __table_args__ = (
        CheckConstraint('release_date < CURRENT_DATE', name='check_future'),
    )


class GameSchema(ma.Schema):

    favourites = fields.List(fields.Nested('FavouriteSchema'))
    reviews =  fields.List(fields.Nested('ReviewSchema', exclude = ['game']))
    developer = fields.Nested('DeveloperSchema', only=['id','name'])


    class Meta:
        fields = ('id', 'title', 'description', 'genre', 'publisher', 'release_date', 'developer', 'reviews')



game_schema = GameSchema()
games_schema = GameSchema(many = True, exclude = ['reviews'])