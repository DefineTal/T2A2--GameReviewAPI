from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length


class User(db.Model):
    __tablename__ = "users"

    # Model 
    id = db.Column(db.Integer, primary_key = True )
    username = db.Column(db.String, nullable = False, unique=True)
    password = db.Column(db.String, nullable = False)
    is_admin = db.Column(db.Boolean, default = False)

    favourites = db.relationship('Favourite', back_populates = 'user', cascade = 'all, delete')
    reviews = db.relationship('Review', back_populates = 'user', cascade = 'all, delete')

# Schema 
class UserSchema(ma.Schema):

    username = fields.String(required = True, validate = Length(min = 1))
    password = fields.String(required = True, validate = Length(min = 4)) 

    favourites = fields.List(fields.Nested('FavouriteSchema'))
    reviews = fields.List(fields.Nested('ReviewSchema'))
    

    class Meta:
        fields = ("id", "username", "password", "is_admin", "favourites")

user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(many = True, exclude = ["password", "favourites"])