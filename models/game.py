from init import db, ma

class Game(db.Model):
    __tablename_ = "games"

    # Model
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(20))
    publisher = db.Column(db.String(25))
    release_date = db.Column(db.String(8))