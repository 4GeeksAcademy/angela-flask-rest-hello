from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }
    
class Characters(db.Model):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    height = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Characters {self.id} {self.name}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height
        }

class Planets(db.Model):
    __tablename__ = "planets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    population = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Planet {self.id} {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population
        }

class FavoritePlanets(db.Model):
    __tablename__ = "favorite_planets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_relationship = db.relationship(User)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    planet_id_relationship = db.relationship(Planets)

    def __repr__(self):
        return f'<FavoritePlanets user_id={self.user_id} planet_id={self.planet_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }
    
class FavoriteCharacters(db.Model):
    __tablename__ = "favorite_characters"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id_relationship = db.relationship(User)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    character_id_relationship = db.relationship(Characters)

    def __repr__(self):
        return f'<FavoriteCharacters user_id={self.user_id} character_id{self.character_id}'
    
    def serialize(self):
        return{
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }