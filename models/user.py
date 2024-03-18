from init import db, ma
from marshmallow import fields


class User(db.Model):
    __tablename__ = "users"

    # Model 
    id = db.Column(db.Integer, primary_key = True )
    username = db.Column(db.String, nullable = False, unique=True)
    password = db.Column(db.String, nullable = False)
    is_admin = db.Column(db.Boolean, default = False)

    favourites = db.relationship('Favourite', back_populates = 'user', cascade = 'all, delete')

# Schema 
class UserSchema(ma.Schema):

    favourites = fields.List(fields.Nested('FavouriteSchema'))

    class Meta:
        fields = ("id", "username", "password", "is_admin")

user_schema = UserSchema(exclude = ["password"])
users_schema = UserSchema(many = True, exclude = ["password"])