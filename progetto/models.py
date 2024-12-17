from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Modello per l'utente
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Modello per le carte
class ListaCarte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) 
    descrizione = db.Column(db.String(100), nullable=False)
    prezzo = db.Column(db.Float, nullable=False)

# Tabella di associazione per il rapporto molti-a-molti
deck_carte = db.Table('deck_carte',
    db.Column('deck_id', db.Integer, db.ForeignKey('deck.id'), primary_key=True),
    db.Column('carta_id', db.Integer, db.ForeignKey('lista_carte.id'), primary_key=True)
)

# Modello per il mazzo di carte
class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)  # Nome del mazzo
    descrizione = db.Column(db.String(200), nullable=True)  # Descrizione opzionale
    carte = db.relationship('ListaCarte', secondary=deck_carte, backref='mazzi')
