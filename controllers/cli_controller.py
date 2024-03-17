from flask import Blueprint
from init import db, bcrypt
from models.user import User
from models.developer import Developer
from sqlalchemy.exc import IntegrityError

db_commands = Blueprint('db', __name__)


# create tables
@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables Created!")


# delete created tables
@db_commands.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables Dropped!")


# add data to created tables
@db_commands.cli.command('seed')
def seed_tables():
    users = [
        User(
            username = "jamesthegamer",
            password = bcrypt.generate_password_hash("owned1234").decode('utf-8')
        ),
        User(
            username = "stevefromaccounting",
            password = bcrypt.generate_password_hash("bigmoney12").decode('utf-8')
        ),       
        User(
            username = "admintest",
            password = bcrypt.generate_password_hash("12345").decode('utf-8'),
            is_admin = True
        )        
    ]

    db.session.add_all(users)

    developers = [
        Developer(
            name = "Notactvision",
            date_founded = "15/12/15"
        ),
        Developer(
            name = "Red Fist Games",
            date_founded = "19/11/96"
        )
    ]

    db.session.add_all(developers)

    try:
        db.session.commit()
        print("Tables Seeded!")

    except IntegrityError as e:
        print("Integrity Error")
        print("Tables failed to seed!")
