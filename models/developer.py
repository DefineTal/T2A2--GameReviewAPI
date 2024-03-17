from init import db, ma
from sqlalchemy import CheckConstraint, func
from datetime import datetime

class Developer(db.Model):

    __tablename__ = "developers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    date_founded = db.Column(db.Date)

    __table_args__ = (
        CheckConstraint('date_founded < CURRENT_DATE', name='check_future'),
    )

class DeveloperSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "date_founded")

developer_schema = DeveloperSchema()
developers_schema = DeveloperSchema(many=True)
