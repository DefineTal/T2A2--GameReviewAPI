import os
from flask import Flask
from init import db, ma, bcrypt, jwt 

# Function to create the app instance
def create_app():
    app = Flask(__name__)

    # config
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

    # connect libaries from init to the instance
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # init db controller
    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)


    return app
    