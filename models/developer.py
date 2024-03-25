from init import db, ma

from sqlalchemy import CheckConstraint
from marshmallow import fields
from marshmallow.validate import Length


class Developer(db.Model):

    __tablename__ = "developers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique = True)
    date_founded = db.Column(db.Date)

    games = db.relationship('Game', back_populates = 'developer', cascade = 'all, delete')

    __table_args__ = (
        CheckConstraint('date_founded < CURRENT_DATE', name='check_future'),
    )

class DeveloperSchema(ma.Schema):

    name = fields.String(required = True, validate = Length(min = 1))

    games = fields.List(fields.Nested('GameSchema', exclude=['genre', 'publisher', 'release_date','developer']))
    
    class Meta:
        fields = ("id", "name", "date_founded", "games")

developer_schema = DeveloperSchema()
developers_schema = DeveloperSchema(many=True, exclude=["games"])
