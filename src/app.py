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
from models import db, User, Planet, Character, Favorite

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

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ========== ENDPOINTS DE CONSULTA ==========

@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# ========== ENDPOINTS DE FAVORITOS ==========

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required as query parameter"}), 400
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required in request body"}), 400
    
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites", "favorite": favorite.serialize()}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required in request body"}), 400
    
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    favorite = Favorite(user_id=user_id, character_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "People added to favorites", "favorite": favorite.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required in request body"}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Planet removed from favorites"}), 200
    return jsonify({"error": "Favorite not found"}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required in request body"}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "People removed from favorites"}), 200
    return jsonify({"error": "Favorite not found"}), 404

# ========== ENDPOINTS CRUD PARA PLANETS ==========

@app.route('/planet', methods=['POST'])
def create_planet():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
    
    planet = Planet(
        name=data['name'],
        climate=data.get('climate'),
        population=data.get('population')
    )
    
    db.session.add(planet)
    db.session.commit()
    return jsonify({"msg": "Planet created", "planet": planet.serialize()}), 201

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    data = request.get_json()
    if 'name' in data:
        planet.name = data['name']
    if 'climate' in data:
        planet.climate = data['climate']
    if 'population' in data:
        planet.population = data['population']
    
    db.session.commit()
    return jsonify({"msg": "Planet updated", "planet": planet.serialize()}), 200

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted"}), 200

# ========== ENDPOINTS CRUD PARA PEOPLE ==========

@app.route('/people', methods=['POST'])
def create_people():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({"error": "Name is required"}), 400
    
    character = Character(
        name=data['name'],
        height=data.get('height'),
        weight=data.get('weight')
    )
    
    db.session.add(character)
    db.session.commit()
    return jsonify({"msg": "Character created", "character": character.serialize()}), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_people(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    data = request.get_json()
    if 'name' in data:
        character.name = data['name']
    if 'height' in data:
        character.height = data['height']
    if 'weight' in data:
        character.weight = data['weight']
    
    db.session.commit()
    return jsonify({"msg": "Character updated", "character": character.serialize()}), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    db.session.delete(character)
    db.session.commit()
    return jsonify({"msg": "Character deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)