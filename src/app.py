from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, FavoritePlanets, Planets, Characters, FavoriteCharacters
import os

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

@app.route('/user', methods=['GET'])
def handle_hello():
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users]), 200

@app.route("/user/<int:id>", methods=['GET'])
def get_single_user(id):
    single_user = User.query.get(id)
    if single_user is None:
        return jsonify({"msg": "el usuario con el ID: {} no existe".format(id)}), 400
    return jsonify({"data": single_user.serialize()}), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": f"El usuario con ID {user_id} no existe"}), 404

    favorite_planets = FavoritePlanets.query.filter_by(user_id=user_id).all()
    favorite_characters = FavoriteCharacters.query.filter_by(user_id=user_id).all()

    favorite_planets_serialized = [favorite_planet.serialize() for favorite_planet in favorite_planets]
    favorite_characters_serialized = [favorite_character.serialize() for favorite_character in favorite_characters]

    return jsonify({
        "msg": "OK", 
        "data": {
            "planets": favorite_planets_serialized, 
            "characters": favorite_characters_serialized
        }
    }), 200

@app.route("/planets", methods=["POST"])
def new_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "debes enviar informacion en el body"}), 400
    if "name" not in body:
        return jsonify({"msg": "el campo name es obligatorio"}), 400
    if "population" not in body:
         return jsonify({"msg": "el campo population es obligatorio"}), 400
    
    new_planet = Planets()
    new_planet.name = body["name"]
    new_planet.population = body["population"]
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"msg": "nuevo planeta creado",
                    "data": new_planet.serialize()}), 201

@app.route("/planets", methods=["GET"])
def get_planet():
    all_planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in all_planets]), 200

@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_single_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": f"El planeta con ID {planet_id} no existe"}), 404
    return jsonify({"data": planet.serialize()}), 200

@app.route("/characters", methods=["POST"])
def new_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "debes enviar informacion en el body"}), 400
    if "name" not in body:
        return jsonify({"msg": "el campo name es obligatorio"}), 400
    if "height" not in body:
         return jsonify({"msg": "el campo height es obligatorio"}), 400

    new_character = Characters()
    new_character.name = body["name"]
    new_character.height = body["height"]
    db.session.add(new_character)
    db.session.commit()

    return jsonify({"msg": "nuevo personaje creado",
                    "data": new_character.serialize()}), 201

@app.route("/characters", methods=["GET"])
def get_character():
    all_characters = Characters.query.all()
    return jsonify([character.serialize() for character in all_characters]), 200

@app.route("/characters/<int:character_id>", methods=["GET"])
def get_single_character(character_id):
    character = Characters.query.get(character_id)
    if character is None:
        return jsonify({"msg": f"El personaje con el ID {character_id} no existe"}), 404
    return jsonify({"data": character.serialize()}), 200

@app.route("/user/<int:user_id>/favoritecharacters", methods=["POST"])
def create_favorite_character(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": f"El usuario con ID {user_id} no existe"}), 404
    
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "debes enviar informacion en el body"}), 400
    if "character_id" not in body:
        return jsonify({"msg": "el campo character_id es obligatorio"}), 400

    character_id = body["character_id"]
    character = Characters.query.get(character_id)
    if character is None:
        return jsonify({"msg": f"El personaje con el ID {character_id} no existe"}), 404

    favorite_character = FavoriteCharacters(user_id=user_id, character_id=character_id)
    db.session.add(favorite_character)
    db.session.commit()

    return jsonify({"msg": "Personaje favorito añadido", "data": favorite_character.serialize()}), 201

@app.route("/user/<int:user_id>/favoriteplanets", methods=["POST"])
def create_favorite_planet(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": f"El usuario con ID {user_id} no existe"}), 404
    
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg":"debes enviar informacion en el body"}), 400
    if "planet_id" not in body:
        return jsonify({"msg": "el campo planet_id es obligatorio"}), 400
    
    planet_id = body["planet_id"]
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": f"El planeta con el ID {planet_id} no existe"}), 400
    
    favorite_planet = FavoritePlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({"msg": "Planeta favorito añadido", "data": favorite_planet.serialize()}), 201

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    favorite_planet = FavoritePlanets.query.get(planet_id)
    if favorite_planet is None:
        return jsonify({"msg": f"El planeta favorito con ID {planet_id} no existe"}), 404
    
    db.session.delete(favorite_planet)
    db.session.commit()

    return jsonify({"msg": "Planeta favorito eliminado"}), 200

@app.route("/favorite/character/<int:character_id>", methods=["DELETE"])
def delete_favorite_character(character_id):
    favorite_character= FavoriteCharacters.query.get(character_id)
    if character_id is None:
        return jsonify({"msg": f"El personaje favorito con el ID {character_id} no existe"}), 404
    
    db.session.delete(favorite_character)
    db.session.commit()

    return jsonify({"msg": "Personaje favorito eliminado"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
