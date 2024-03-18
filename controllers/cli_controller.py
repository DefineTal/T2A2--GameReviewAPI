from flask import Blueprint
from init import db, bcrypt
from models.user import User
from models.developer import Developer
from models.game import Game
from models.favourite import Favourite
from sqlalchemy.exc import IntegrityError, DataError

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
            date_founded = "2020/11/15"
        ),
        Developer(
            name = "Red Fist Games",
            date_founded = "1990/8/12"
        )
    ]

    db.session.add_all(developers)


    games = [
        Game(
            title = "Gunblood 3",
            description = "You already know what it is!",
            genre = "Action/Platformer",
            release_date = "2023/1/1",
            developer_id = 1
        ),
        Game(
            title = "Shade, Regends of Ladow",
            description = "omg amazing game with good rate on gacha",
            genre = "Strategy/Gacha",
            release_date = "2018/2/21",
            developer_id = 2
        )
    ]

    db.session.add_all(games)


    favourites = [
        Favourite(
            user_id = 1,
            game_id = 1
        )
    ]
    
    db.session.add_all(favourites)

    try:
        db.session.commit()
        print("Tables Seeded!")

    except IntegrityError as e:
        db.session.rollback()
        print(e)
        print("Tables failed to seed! Integrity Error")

    except DataError as v:
        db.session.rollback()
        print(v)
        print("Tables failed to seed! Data Error")

    
