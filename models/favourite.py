from init import db, ma
from marshmallow import fields

class Favourite(db.Model):
    __tablename__ = "favourites"

    id = db.Column(db.Integer, primary_key = True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable = False)

    user = db.relationship('User', back_populates = 'favourites')
    game = db.relationship('Game', back_populates = 'favourites')

class FavouriteSchema(ma.Schema):

    user = fields.Nested('UserSchema', only=['username'], required=True)
    game = fields.Nested('GameSchema', only=['title'], required=True)

    class Meta:
        fields = ('id','user','game')


favourite_schema = FavouriteSchema()
favourites_schema = FavouriteSchema(many = True)