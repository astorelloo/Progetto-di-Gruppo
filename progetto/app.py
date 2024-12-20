from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from models import db, User, ListaCarte
app = Flask(__name__)
app.secret_key = 'key_sessione_user' #chiave per la sessione user
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#inizializza db e flask-login
db.init_app(app)
login_manager = LoginManager() #inizializza flask-login
login_manager.init_app(app) #collega flask-login e flask
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'] #prende dati dalle form
        password = request.form['password']
        #check se l'utente esiste nel db
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già inuso.")
        #crea user e lo salva nel db
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] #prende dati dalle form
        password = request.form['password']
        #cerca user db
        user = User.query.filter_by(username=username, password=password).first()
        if user: #se user esiste
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Credenziali nonvalide.") #errore se credenziali errate
    return render_template('login.html', error=None)

@app.route('/home')
@login_required #solo se user è autenticato
def home():
    return render_template('home.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user() #logout user
    return redirect(url_for('login')) #torniamo al login

@app.route('/api/carte', methods=['GET'])
def get_carte():
    carte = ListaCarte.query.all()
    return {
        "carte": [
            {"id": carta.id, "nome": carta.nome, "descrizione": carta.descrizione, "prezzo": carta.prezzo}
            for carta in carte
        ]
    }

API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

def fetch_and_populate():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        carte = data.get("data", [])[:100]  # Prendi le prime 100 carte
        with app.app_context():
           for carta in carte:
                nome = carta.get("name", "Sconosciuto")
                descrizione = carta.get("desc", "Nessuna descrizione")
                prezzo = carta.get("card_prices", [{}])[0].get("amazon_price", 0.0)
                foto = carta.get("card_images", [{}])[0].get("image_url", None)
               
                nuova_carta = ListaCarte(
                    nome=nome,
                    descrizione=descrizione,
                    prezzo=float(prezzo) if prezzo else 0.0,
                    foto=foto
                )
                #crea user e lo salva nel db
                new_carta = carta(nome =nome, descrizione=descrizione, prezzo = prezzo, foto = foto)
                db.session.add(new_carta)
                db.session.commit()
                print("Database popolato con successo!")
    

if __name__ == "__main__":
    app.run(debug=True)
    #fetch_and_populate()
    