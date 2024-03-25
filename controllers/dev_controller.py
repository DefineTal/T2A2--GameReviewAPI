from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db

from models.developer import Developer, developer_schema, developers_schema

from sqlalchemy.exc import IntegrityError, ArgumentError
from psycopg2 import errorcodes

from marshmallow import ValidationError


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
    
@dev_bp.route('/', methods=["POST"])
@jwt_required()
def create_dev():
    try:
        body_data = developer_schema.load(request.get_json())
        dev = Developer(
            name = body_data.get('name'),
            date_founded = body_data.get('date_founded')
        )

        db.session.add(dev)
        db.session.commit()
        return developer_schema.dump(dev)
      
    except ValidationError as val_err:
        return {"error": str(val_err)}, 400
  
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Developer name already recorded!"}, 409
        
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 409
        
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid date try again!"}, 409
        
        return {"error": "An integrity error occurred"}, 500
       
    except:
        return {"error": "Data error. Try again!"}, 409
    

@dev_bp.route('/<int:dev_id>', methods = ["DELETE"])
@jwt_required()
def delete_dev(dev_id):
    stmt = db.select(Developer).where(Developer.id == dev_id)
    dev = db.session.scalar(stmt)
    if dev:
        db.session.delete(dev)
        db.session.commit()
        return {'message': f"dev {dev.name} deleted successfully"}
    else:
        db.session.rollback()
        return {'error': f"dev with id {dev_id} not found"}, 404
    

@dev_bp.route('/<int:dev_id>', methods = ["PUT", "PATCH"])
@jwt_required()
def update_dev(dev_id):
    try:
        body_data = developer_schema.load(request.get_json())
        stmt = db.select(Developer).filter_by(id = dev_id)
        dev = db.session.scalar(stmt)
        if dev:
            dev.name = body_data.get('name') or dev.name
            dev.date_founded = body_data.get('date_founded') or dev.date_founded

            db.session.commit()
            return developer_schema.dump(dev)
    
        else:
            return {'error': f"dev with id {dev_id} not found"}, 404
    
    except ValidationError as val_err:
        db.session.rollback()
        return {"error": str(val_err)}, 400
    
    except IntegrityError as err:
        db.session.rollback()

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"Developer name {dev.name} already recorded!"}, 409
        
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid date try again!"}, 409
    