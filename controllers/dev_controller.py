from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db

from models.developer import Developer, developer_schema, developers_schema

from sqlalchemy.exc import IntegrityError, ArgumentError
from psycopg2 import errorcodes

from marshmallow import ValidationError


dev_bp = Blueprint('developers', __name__, url_prefix='/developers/')


# Method=Get
# Endpoint=/developers
# Gets all developers
@dev_bp.route('/')
def get_all_devs():
    # selects all devs and gets ready to order them
    stmt = db.select(Developer).order_by(Developer.id.asc())
    developers = db.session.scalars(stmt)
    # returns list to user
    return developers_schema.dump(developers)


# Method=Get
# Endpoint=/developers/<developer_id>
# Gets a developer
@dev_bp.route('/<int:developer_id>')
def get_dev(developer_id):
    # finds dev with id matching url
    stmt = db.select(Developer).filter_by(id=developer_id)
    developer = db.session.scalar(stmt)
    # if exists -> return dev, else return error
    if developer:
        return developer_schema.dump(developer)
    else:
        return{"error": f"user id {developer_id} doesn't exist. Please try again"}, 404


# Method=Post
# Endpoint=/developers/<developer_id>
# Creates a developer
@dev_bp.route('/', methods=["POST"])
@jwt_required()
def create_dev():
    try:
        # gather data from json input field and check if it is compatiable with imported schema
        body_data = developer_schema.load(request.get_json())
        # use data to create dev instance -> commit instance to database -> return the instance to user
        dev = Developer(
            name = body_data.get('name'),
            date_founded = body_data.get('date_founded')
        )

        db.session.add(dev)
        db.session.commit()
        return developer_schema.dump(dev)
    
    # error catches for different types of errors
    except ValidationError as val_err:
        return {"error": str(val_err)}, 400
  
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Developer name already recorded!"}, 409
        
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"{err.orig.diag.column_name} is null, make sure to input a value!"}, 400
        
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid date try again!"}, 409
        
        return {"error": "An integrity error occurred"}, 400
       
    except:
        return {"error": "Data error. Try again!"}, 409
    

# Method=Delete
# Endpoint=/developers/<developer_id>
# Deletes a developer
@dev_bp.route('/<int:dev_id>', methods = ["DELETE"])
@jwt_required()
def delete_dev(dev_id):
    # finds dev with same id as in url
    stmt = db.select(Developer).where(Developer.id == dev_id)
    dev = db.session.scalar(stmt)
    # if dev exists -> delete dev, if not return error
    if dev:
        db.session.delete(dev)
        db.session.commit()
        return {'message': f"dev {dev.name} deleted successfully"}
    else:
        db.session.rollback()
        return {'error': f"dev with id {dev_id} not found"}, 404
    

# Method =Put, Patch
# Endpoint=/developers/<developer_id>
# Updates a developers details
@dev_bp.route('/<int:dev_id>', methods = ["PUT", "PATCH"])
@jwt_required()
def update_dev(dev_id):
    try:
        # store json input data
        body_data = developer_schema.load(request.get_json())
        # find dev with id matching url
        stmt = db.select(Developer).filter_by(id = dev_id)
        dev = db.session.scalar(stmt)
        # if dev exist -> compare input with existing instance, else return error
        if dev:
            dev.name = body_data.get('name') or dev.name
            dev.date_founded = body_data.get('date_founded') or dev.date_founded

            db.session.commit()
            return developer_schema.dump(dev)
    
        else:
            return {'error': f"dev with id {dev_id} not found"}, 404
        
    # error catches for different types of errors
    except ValidationError as val_err:
        db.session.rollback()
        return {"error": str(val_err)}, 400
    
    except IntegrityError as err:
        db.session.rollback()

        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"Developer name {dev.name} already recorded!"}, 409
        
        if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
            return {"error": "Invalid date try again!"}, 409
    