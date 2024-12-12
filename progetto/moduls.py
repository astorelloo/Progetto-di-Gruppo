from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy() 
class lista_carte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) 
    descrizione = db.Column(db.String(100), nullable = False)
    immagine = db.Column(db)
class ListaUtenti(db.Model):
    nome = db.Column(db.String(100), primary_key = True)
    password = db.Column(db.String(100), primary_key = True)