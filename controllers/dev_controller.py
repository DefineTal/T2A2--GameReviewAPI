from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.developer import Developer, developer_schema, developers_schema

dev_bp = Blueprint('developers', __name__, url_prefix='/developers/')

@dev_bp.route('/')
def get_all_devs():
    stmt = db.select(Developer).order_by(Developer.id.asc())
    developers = db.session.scalars(stmt)
    return developers_schema.dump(developers)

@dev_bp.route('/<int:developer_id>')
def get_dev(developer_id):
    stmt = db.select(Developer).filter_by(id=developer_id)
    developer = db.session.scalar(stmt)
    if developer:
        return developer_schema.dump(developer)
    else:
        return{"error": f"user id {developer_id} doesn't exist. Please try again"}, 404