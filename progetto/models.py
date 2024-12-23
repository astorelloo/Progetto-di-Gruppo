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
#----------------------------------------------------------------------------------------
# Tabella di associazione tra Deck e Carta con una colonna per la quantità
class DeckCarta(db.Model):
    __tablename__ = 'deck_carta'
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    carta_id = db.Column(db.Integer, db.ForeignKey('carta.id'), nullable=False) 
    quantita = db.Column(db.Integer, nullable=False, default=1)

# Modello per il mazzo
class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descrizione = db.Column(db.String(200), nullable=True)
    
    # Relazione con DeckCarta per accedere alle carte associate e alla loro quantità
    carte = db.relationship('DeckCarta', backref='deck', lazy=True)
#----------------------------------------------------------------------------------------
class CarrelloItem(db.Model):
    __tablename__ = 'carrello_item'
    id = db.Column(db.Integer, primary_key=True)  # Chiave primaria per ogni elemento del carrello
    carrello_id = db.Column(db.Integer, db.ForeignKey('carrello.id'), nullable=False)
    carta_id = db.Column(db.Integer, db.ForeignKey('carta.id'), nullable=False)
    quantita = db.Column(db.Integer, nullable=False, default=1)
    # Relazioni per accesso facilitato
    carta = db.relationship('Carta', backref='carrello_items', lazy=True)

class Carrello(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID dell'utente proprietario del carrello
    # Relazione con l'utente
    user = db.relationship('User', backref='carrello', lazy=True)
    # Relazione con gli elementi del carrello
    items = db.relationship('CarrelloItem', backref='carrello', lazy=True)
