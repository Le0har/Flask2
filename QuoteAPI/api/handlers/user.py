from api import app, db
from api.models.user import UserModel
from api.schemas.user import user_schema, users_schema
from flask import abort, jsonify, request
from marshmallow import ValidationError


# url: /users
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.loads(request.data) # get_data
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
    except ValidationError as ve:
        abort(400, f'Validation error: {str(ve)}')
    except Exception as e:
        db.session.rollback()
        abort(503, f'Database error: {str(e)}')
    return jsonify(user_schema.dump(user)), 201


# url: /users
@app.route('/users', methods=['GET'])
def get_users():
    users_db = db.session.scalars(db.select(UserModel)).all()
    return jsonify(users_schema.dump(users_db)), 200


# url: /users/<int:user_id>
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = db.get_or_404(UserModel, user_id, description=f'User with id={user_id} not found')
    return jsonify(user_schema.dump(user)), 200