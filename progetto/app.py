#si importano tutte le cose necessarie
from flask import Flask, render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from moduls import db, lista_carte
app = Flask(__name__)
#si configura sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lista_carte.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#si inizializza il db e lo si crea se non ce
db.init_app(app)
with app.app_context():
    db.create_all()

carte= []
@app.route('/')
def home():
    #metodo che ci carica la pagina
   #carte = carte.query.all()
    return render_template('index.html' , lista_carte = carte)

#accesso
@app.route('/registrazione', methods=['POST'])
def registrazione():
    nome = request.form.get('nome')
    password = request.form.get('password')
    if nome:
        nuovo_elemento = ListaUtenti(nome =nome, password= password)
        db.session.add(nuovo_elemento) 
        db.session.commit() 
    return render_template('home.html' , lista_carte = carte)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        password = request.form.get('password')

        if not nome or not password:
            errore = "Inserisci sia il nome utente che la password."
            return render_template('index.html', errore=errore)
        utente = ListaUtenti.query.filter_by(nome=nome, password=password).first()
        if utente:
            return render_template('home.html', lista_carte=carte)
        else:
            errore = "Nome utente o password errati."
            return render_template('index.html', errore=errore)
    # Se il metodo è GET, mostra la pagina di login
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)