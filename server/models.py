from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    missions = db.relationship('Mission', back_populates='planet', cascade='all, delete-orphan')
    scientists = association_proxy('missions', 'scientist')

    serialize_rules = ('-missions.planet',)

    def __repr__(self):
        return f'<Planet {self.id}: {self.name}>'

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    field_of_study = db.Column(db.String(100), nullable=False)

    missions = db.relationship('Mission', back_populates='scientist', cascade='all, delete-orphan')
    planets = association_proxy('missions', 'planet')

    serialize_rules = ('-missions.scientist',)

    @validates('name', 'field_of_study')
    def validate_not_empty(self, key, value):
        if not value or value.strip() == '':
            raise ValueError(f'{key} cannot be empty')
        return value

    def __repr__(self):
        return f'<Scientist {self.id}: {self.name}>'

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    mission_date = db.Column(db.Date, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    planet = db.relationship('Planet', back_populates='missions')
    scientist = db.relationship('Scientist', back_populates='missions')

    serialize_rules = ('-planet.missions', '-scientist.missions')

    @validates('duration_days')
    def validate_duration(self, key, value):
        if value <= 0:
            raise ValueError('Mission duration must be positive')
        return value

    @validates('mission_date')
    def validate_mission_date(self, key, value):
        from datetime import date
        if value < date.today():
            raise ValueError('Mission date must be in the future')
        return value

    def __repr__(self):
        return f'<Mission {self.id}: {self.scientist.name} to {self.planet.name}>'
