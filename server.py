# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
app = Flask(__name__)
# We'll just use SQLite here so we don't need an external database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/development.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'please, tell nobody... Shhhh'
app.config['LOGGING_LEVEL'] = logging.INFO

# Pull options from environment
debug = (os.getenv('DEBUG', 'False') == 'True')
port = os.getenv('PORT', '5000')

db = SQLAlchemy(app)

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

######################################################################
# ERROR Handling
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(e):
    return make_response(jsonify(status=400, error='Bad Request', message=e.message), status.HTTP_400_BAD_REQUEST)

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify(status=404, error='Not Found', message=e.description), status.HTTP_404_NOT_FOUND)

@app.errorhandler(400)
def bad_request(e):
    return make_response(jsonify(status=400, error='Bad Request', message=e.message), status.HTTP_400_BAD_REQUEST)

@app.errorhandler(405)
def method_not_allowed(e):
    return make_response(jsonify(status=405, error='Method not Allowed', message='Your request method is not supported. Check your HTTP method and try again.'), status.HTTP_405_METHOD_NOT_ALLOWED)

@app.errorhandler(500)
def internal_error(e):
    return make_response(jsonify(status=500, error='Internal Server Error', message='Huston... we have a problem.'), status.HTTP_500_INTERNAL_SERVER_ERROR)

######################################################################
# Pet Model for database
######################################################################
class Pet(db.Model):
    """A single pet"""
    __tablename__ = "pets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))

    def self_url(self):
        return url_for('get_pets', id=self.id, _external=True)

    def serialize(self):
        return { "id": self.id, "name": self.name, "category": self.category }

    def deserialize(self, data):
        try:
            self.name = data['name']
            self.category = data['category']
        except KeyError as e:
            raise DataValidationError('Invalid pet: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid pet: body of request contained bad or no data')
        return self

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    # data = '{name: <string>, category: <string>}'
    # url = request.base_url + 'pets' # url_for('list_pets')
    # return jsonify(name='Pet Demo REST API Service', version='1.0', url=url, data=data), status.HTTP_200_OK
    return app.send_static_file('index.html')

######################################################################
# LIST ALL PETS
######################################################################
@app.route('/pets', methods=['GET'])
def list_pets():
    pets = []
    category = request.args.get('category')
    if category:
        pets = Pet.query.filter(Pet.category == category)
    else:
        pets = Pet.query.all()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/pets/<int:id>', methods=['GET'])
def get_pets(id):
    pet = Pet.query.get(id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(id))
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pets():
    pet = Pet()
    pet.deserialize(request.get_json())
    db.session.add(pet)
    db.session.commit()
    message = pet.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED, {'Location': pet.self_url() })

######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<int:id>', methods=['PUT'])
def update_pets(id):
    pet = Pet.query.get_or_404(id)
    pet.deserialize(request.get_json())
    db.session.commit()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<int:id>', methods=['DELETE'])
def delete_pets(id):
    pet = Pet.query.get(id)
    if pet:
        db.session.delete(pet)
        db.session.commit()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        handler = logging.StreamHandler()
        handler.setLevel(app.config['LOGGING_LEVEL'])
        # formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        #'%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

######################################################################
# INITIALIZE Redis
# This method will work in the following conditions:
#   1) In Bluemix with Redis bound through VCAP_SERVICES
#   2) With Redis running on the local server as with Travis CI
#   3) With Redis --link ed in a Docker container called 'redis'
######################################################################
# def inititalize_redis():
#     global redis
#     redis = None
#     # Get the crdentials from the Bluemix environment
#     if 'VCAP_SERVICES' in os.environ:
#         app.logger.info("Using VCAP_SERVICES...")
#         VCAP_SERVICES = os.environ['VCAP_SERVICES']
#         services = json.loads(VCAP_SERVICES)
#         creds = services['rediscloud'][0]['credentials']
#         app.logger.info("Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port']))
#         redis = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
#     else:
#         app.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
#         redis = connect_to_redis('127.0.0.1', 6379, None)
#         if not redis:
#             app.logger.info("No Redis on localhost, using: redis")
#             redis = connect_to_redis('redis', 6379, None)
#     if not redis:
#         # if you end up here, redis instance is down.
#         app.logger.error('*** FATAL ERROR: Could not connect to the Redis Service')
#         exit(1)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "Pet Service Starting..."
    db.create_all()  # make our sqlalchemy tables
    app.run(host='0.0.0.0', port=int(port), debug=debug)
