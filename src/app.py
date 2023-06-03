"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite_People, Favorite_Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# my enpoints here

@app.route('/user', methods=['GET'])
def get_user():

    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200 

@app.route('/user', methods=['POST'])
def create_user():
    request_body_user = request.get_json()

    new_user = User(first_name=request_body_user["first_name"], last_name=request_body_user["last_name"], email=request_body_user["email"], password=request_body_user["password"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify(request_body_user), 200 

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    user1 = User.query.get(user_id)
    if user1 is None:
        raise APIException("User not found", status_code=404)
    db.session.delete(user1)
    db.session.commit()

    return jsonify("ok"), 200 


@app.route('/people', methods=['GET'])
def get_people():

    peoples = People.query.all()
    all_people = list(map(lambda x: x.serialize(), peoples))
    return jsonify(all_people), 200 


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_detail(people_id):

    person = People.query.get(people_id)
    if person:
        person_detail = person.serialize()
        return jsonify(person_detail), 200
    else:
        return jsonify({"message": "Person not found"}), 404


@app.route('/planet', methods=['GET'])
def get_planet():

    planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))
    return jsonify(all_planets), 200 


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_detail(planet_id):

    planet1 = Planet.query.get(planet_id)
    if planet1:
        planet_detail = planet1.serialize()
        return jsonify(planet_detail), 200
    else:
        return jsonify({"message": "Planet not found"}), 404

@app.route('/favorite/', methods=['GET'])
def get_favorites():
    favoritesPlanet = Favorite_Planet.query.all()
    favoritesPeople = Favorite_People.query.all()
    all_favoritePlanet = list(map(lambda x: x.serialize(), favoritesPlanet))
    all_favoritePeople = list(map(lambda x: x.serialize(), favoritesPeople))
    return jsonify({"planets": all_favoritePlanet}, {"people": all_favoritePeople} ), 200 

@app.route('/favorite/people/', methods=['GET'])
def get_favorite_people():
    favoritesPeople = Favorite_People.query.all()
    all_favoritePeople = list(map(lambda x: x.serialize(), favoritesPeople))
    return jsonify(all_favoritePeople), 200 

@app.route('/favorite/people/', methods=['POST'])
def add_favorite_people():
    request_body_Favorite_People = request.get_json()

    new_favoritePeople = Favorite_People(user_id=request_body_Favorite_People["user_id"], people_id=request_body_Favorite_People["people_id"])
    print(new_favoritePeople)
    db.session.add(new_favoritePeople)
    db.session.commit()
    response={"msg": "Its OK"}
    return jsonify(response), 200 


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):

    to_delete = Favorite_People.query.filter_by(people_id= people_id).first()
    if to_delete is None:
        raise APIException("Favorite character not found", status_code=404)
    db.session.delete(to_delete)
    db.session.commit()

    return jsonify("Favorite character deletion successful"), 200

@app.route('/favorite/planet/', methods=['GET'])
def get_favorite_planet():
    favoritesPlanet = Favorite_Planet.query.all()
    all_favoritePlanet = list(map(lambda x: x.serialize(), favoritesPlanet))
    return jsonify(all_favoritePlanet), 200 

@app.route('/favorite/planet/', methods=['POST'])
def add_favorite_planet():
    request_body_Favorite_Planet = request.get_json()

    new_favoritePlanet = Favorite_Planet(user_id=request_body_Favorite_Planet["user_id"], planet_id=request_body_Favorite_Planet["planet_id"])
    print(new_favoritePlanet)
    db.session.add(new_favoritePlanet)
    db.session.commit()
    response={"msg": "Its OK"}
    return jsonify(response), 200 


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    to_delete = Favorite_Planet.query.filter_by(planet_id= planet_id).first()
    if to_delete is None:
        raise APIException("Favorite planet not found", status_code=404)
    db.session.delete(to_delete)
    db.session.commit()

    return jsonify("Favorite planet deletion successful"), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)