#!/usr/bin/env python3

import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Scientist, Mission, Planet


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Interplanetary Booking System!"})

class ScientistResource(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return jsonify([s.to_dict() for s in scientists])

    def post(self):
        data = request.get_json()
        new_scientist = Scientist(name=data["name"], field_of_study=data["field_of_study"])
        db.session.add(new_scientist)
        db.session.commit()
        return jsonify(new_scientist.to_dict()), 201

class PlanetResource(Resource):
    def get(self):
        planets = Planet.query.all()
        return jsonify([p.to_dict() for p in planets])

class MissionResource(Resource):
    def get(self):
        missions = Mission.query.all()
        return jsonify([m.to_dict() for m in missions])

    def post(self):
        data = request.get_json()
        new_mission = Mission(name=data["name"], planet_id=data["planet_id"], scientist_id=data["scientist_id"])
        db.session.add(new_mission)
        db.session.commit()
        return jsonify(new_mission.to_dict()), 201

# Add API resources
api.add_resource(ScientistResource, "/scientists")
api.add_resource(PlanetResource, "/planets")
api.add_resource(MissionResource, "/missions")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
