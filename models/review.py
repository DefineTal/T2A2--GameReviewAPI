from init import db, ma
from marshmallow import fields

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key = True)
    rating = db.Column(db.Integer, nullable = False)
    date_made = db.Column(db.Date, default=db.func.current_date())
    completed = db.Column(db.Boolean)
    content = db.Column(db.Text)


    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable = False)

    user = db.relationship('User', back_populates = 'reviews')
    game = db.relationship('Game', back_populates = 'reviews')

    __table_args__ = (
        db.CheckConstraint('rating > 0 AND rating < 11', name='check_value_range')
    )

class ReviewSchema(ma.Schema):
    
    user = fields.Nested('UserSchema', only = ['username'])

    game = fields.Nested('GameSchema', only = ['title']) 

    class Meta:
        fields = ('id', 'user', 'game', 'rating', 'date_made', 'completed', 'content')


review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many = True)