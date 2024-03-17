from init import db, ma
from sqlalchemy import CheckConstraint

class Developer(db.Model):

    __tablename__ = "developer"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(25), nullable = False)
    date_founded = db.Column(db.String(8))

    __table_args__ = (
        CheckConstraint("date_founded ~ '^\d{2}/\d{2}/\d{2}$'", name='check_date_format'),
    )

class DeveloperSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "date_founded")

developer_schema = DeveloperSchema()
developers_schema = DeveloperSchema(many = True)