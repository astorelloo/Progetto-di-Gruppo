from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Deck, Carta, DeckCarta, CarrelloItem, Carrello
import requests

app = Flask(__name__)
app.secret_key = 'key_sessione_user'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Questo username è già in uso.")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Credenziali non valide.")
    return render_template('login.html', error=None)

@app.route('/home')
@login_required
def home():
    carte = Carta.query.all()
    for carta in carte:
        print(carta.nome, carta.foto)  # Debug: stampa il nome e la foto di ogni carta
    return render_template('home.html',carta = carte, username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/deck', methods=['GET', 'POST'])
@login_required
def deck():
    #controllo se il deck esiste per l'utente
    user_deck = Deck.query.filter_by(nome=f"Deck di {current_user.username}").first()
    if not user_deck:
        return render_template('deck.html', username=current_user.username, deckCarte=[], error="Deck non trovato.")
    #da qua in poi onclick del bottone
    if request.method == 'POST':
        carta_id = request.form.get('carta_id')
        print(f"ID carta ricevuto: {carta_id}")

        carta = Carta.query.get(int(carta_id))
        if not carta:
            print(f"Carta non trovata per ID: {carta_id}")
            return render_template('deck.html', username=current_user.username, deckCarte=[], error="Carta non trovata.")

        deck_carta = DeckCarta.query.filter_by(deck_id=user_deck.id, carta_id=carta_id).first()
        print(f"DeckCarta trovato: {deck_carta}")

        if deck_carta:
            if deck_carta.quantita < 3:
                deck_carta.quantita += 1
                db.session.commit()
                print("Quantità aggiornata nel deck.")
            else:
                print("Errore: Massimo 3 copie.")
                return render_template('deck.html', username=current_user.username, deckCarte=[], error="Puoi aggiungere massimo 3 copie di una carta.")
        else:
            nuova_carta = DeckCarta(deck_id=user_deck.id, carta_id=carta_id, quantita=1)
            db.session.add(nuova_carta)
            db.session.commit()
            print("Nuova carta aggiunta al deck.")

    #carica le carte del deck
    deck_carte = DeckCarta.query.filter_by(deck_id=user_deck.id).all()
    carte_dettaglio = [
        {
            "nome": carta.carta.nome,
            "immagine": carta.carta.foto,
            "quantita": carta.quantita
        }
        for carta in deck_carte
        ]
    return render_template('deck.html', username=current_user.username, deckCarte=carte_dettaglio, error=None)


@app.route('/carrello')
@login_required
def carrello():
    return render_template('carrello.html', username=current_user.username, error=None)

@app.route('/api/carte', methods=['GET'])
def get_carte():
    carte = Carta.query.all()
    return {
        "carte": [
            {"id": carta.id, "nome": carta.nome, "descrizione": carta.descrizione, "prezzo": carta.prezzo}
            for carta in carte
        ]
    }

#svuota il db carte e ne mette 1000
API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
def fetch_and_populate():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        carte = data.get("data", [])[:1000]
        with app.app_context():
            for carta in carte:
                nome = carta.get("name", "Sconosciuto")
                descrizione = carta.get("desc", "Nessuna descrizione")
                prezzo = carta.get("card_prices", [{}])[0].get("amazon_price", "0.0")
                foto = carta.get("card_images", [{}])[0].get("image_url", None)

                nuova_carta = Carta(
                    nome=nome,
                    descrizione=descrizione,
                    prezzo=float(prezzo) if prezzo else 0.0,
                    foto=foto
                )
                db.session.add(nuova_carta)
            db.session.commit()
            print("Database popolato con successo!")
def clear_carte():
    with app.app_context():
        # Cancella tutti i record dalla tabella Carta
        num_rows_deleted = Carta.query.delete()
        db.session.commit()
        print(f"Tabella Carte svuotata. {num_rows_deleted} record eliminati.")

if __name__ == "__main__":
    #with app.app_context():
    #    clear_carte()  # Svuota la tabella delle carte
    #    fetch_and_populate()  # Popola la tabella con nuove carte
    app.run(debug=True)
