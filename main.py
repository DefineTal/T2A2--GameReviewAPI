import os
from flask import Flask
from init import db, ma, bcrypt, jwt 

# Function to create the app instance
def create_app():
    app = Flask(__name__)

    app.json.sort_keys = False


    # config
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

    # connect libaries from init to the instance
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Blueprints
    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)

    from controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from controllers.user_controller import users_bp
    app.register_blueprint(users_bp)

    from controllers.dev_controller import dev_bp
    app.register_blueprint(dev_bp)

    from controllers.game_controller import game_bp
    app.register_blueprint(game_bp)

    from controllers.fav_controller import fav_bp
    app.register_blueprint(fav_bp)

    from controllers.review_controller import review_bp
    app.register_blueprint(review_bp)

    return app
    