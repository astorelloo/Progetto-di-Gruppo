#si importano tutte le cose necessarie
from flask import Flask, render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from moduls import db, ListaSpesa
app = Flask(__name__)
#si configura sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lista_spesa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#si inizializza il db e lo si crea se non ce
db.init_app(app)
with app.app_context():
    db.create_all()


carta= []
@app.route('/')
def home():
    #metodo che ci carica la pagina
    carta = Carte.query.all()
    return render_template('index.html' , lista_carte = carta)