from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Carta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.String(100), nullable=False)
    prezzo = db.Column(db.Float, nullable=False)
    foto = db.Column(db.String(200), nullable=True)

deck_carte = db.Table('deck_carte',
    db.Column('deck_id', db.Integer, db.ForeignKey('deck.id'), primary_key=True),
    db.Column('carta_id', db.Integer, db.ForeignKey('carta.id'), primary_key=True)
)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descrizione = db.Column(db.String(200), nullable=True)
    carte = db.relationship('Carta', secondary=deck_carte, backref='mazzi')
