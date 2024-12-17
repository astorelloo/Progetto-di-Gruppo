#si importano tutte le cose necessarie
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from moduls import db, ListaUtenti
app = Flask(__name__)
#si configura sqlalchemy
app.secret_key = 'key_sessione_user' #chiave per la sessione user
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lista_carte.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#si inizializza il db e lo si crea se non ce
db.init_app(app)
login_manager = LoginManager() #inizializza flask-login
login_manager.init_app(app) #collega flask-login e flask
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

carte= []
@app.route('/', methods=['GET', 'POST'])
def home():
    #metodo che ci carica la pagina
   #carte = carte.query.all()
    return render_template('index.html' , lista_carte = carte)

#accesso
@app.route('/registrazione', methods=['POST'])
def registrazione():
    if request.method == 'POST':
        nome = request.form.get('nome')
        password = request.form.get('password')
        #check se l'utente esiste nel db
        if ListaUtenti.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già inuso.")
        #crea user e lo salva nel db
        new_user = ListaUtenti(nome =nome, password= password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get['nome']
        password = request.form.get['password']
        #if not nome or not password:
        #   errore = "Inserisci sia il nome utente che la password."
        #   return render_template('index.html', errore=errore)
        utente = ListaUtenti.query.filter_by(nome=nome, password=password).first()
        if utente:
            login_user(user)
            return render_template('home.html', lista_carte=carte)
        #else:
        #    errore = "Nome utente o password errati."
        #    return render_template('index.html', errore=errore)
    # Se il metodo è GET, mostra la pagina di login
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)