
import os
from tarfile import RECORDSIZE
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


''' @app.route('/')
def hello():
    return "Hello Udacian" '''


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['GET'])
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify ({
        "success": True,
        "drinks": drinks
    })
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details():
    
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
    except AuthError as err:
        abort(422)
          
    return jsonify({
        "status code": 200,
        "success":True,
        "drinks":drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def post_drinks():
    body = request.get_json()
    recipe = body.get('recipe', None)
    title = body.get('title', None)
    try: 
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
    except AuthError as error:
        abort(422)
    return jsonify({
                    "status code": 200,
                    "success":True, 
                    "drinks":[drink.long()]
        })



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(id):
    body = request.get_json()
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    try:
        drink = Drink.query.filter(Drink.id == id).first()
        if not drink:
            abort(404)
        if title:
            drink.title = title
            drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)

            drink.update()
    except Exception as err:
        abort(422)
    return jsonify({
        "status code": 200,
        "success": True, 
        "drinks": [drink.long()]})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(id):
    
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if not drink:
            abort(404)
        drink.delete()
    except:
        abort(422)
    return jsonify({
        "status code": 200,
        "success":True, 
        "deleted":id
        })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, 
        "message": "bad request"
        }), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def resources_not_found(error):
    return jsonify({"success": False, "error": 404, "message": "Not found"}), 404
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(e):
    return (
        jsonify(
            {
                "success": False,
                "error": e.status_code,
                **e.error,
            }
        ),
        e.status_code,
    )
