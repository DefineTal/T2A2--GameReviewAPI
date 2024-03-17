from flask import Blueprint
from init import db, bcrypt
from models.user import User

db_commands = Blueprint('db', __name__)


@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables Created!")


@db_commands.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables Dropped!")


@db_commands.cli.command('seed')
def seed_tables():
    users = [
        User(
            username= "jamesthegamer",
            password= bcrypt.generate_password_hash("owned1234").decode('utf-8')
        ),
        User(
            username= "stevefromaccounting",
            password= bcrypt.generate_password_hash("bigmoney12").decode('utf-8')
        ),       
        User(
            username= "admintest",
            password= bcrypt.generate_password_hash("12345").decode('utf-8'),
            is_admin = True
        )        
    ]

    db.session.add_all(users)
    db.session.commit()

    print("Tables seeded!")