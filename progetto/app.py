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
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_deck':
            print("creazione deck")
            nome_deck = request.form.get('nome_deck')
            descrizione_deck = request.form.get('descrizione_deck', '')
            if Deck.query.filter_by(nome=nome_deck).first():
                return render_template('deck.html', username=current_user.username, deckCarte=[], error="Esiste già un deck con questo nome.")
            
            nuovo_deck = Deck(nome=nome_deck, descrizione=descrizione_deck)
            db.session.add(nuovo_deck)
            db.session.commit()
            return redirect(url_for('deck'))
        
        elif action == 'add_card':
            print("aggiunta carta")
            carta_id = request.form.get('carta_id')
            deck_id = request.form.get('deck_id')
            deck = Deck.query.get(deck_id)
            if not deck:
                return render_template('deck.html', username=current_user.username, deckCarte=[], error="Deck non trovato.")

            carta = Carta.query.get(carta_id)
            if not carta:
                return render_template('deck.html', username=current_user.username, deckCarte=[], error="Carta non trovata.")

            deck_carta = DeckCarta.query.filter_by(deck_id=deck.id, carta_id=carta.id).first()
            if deck_carta:
                if deck_carta.quantita < 3:
                    deck_carta.quantita += 1
                    db.session.commit()
                else:
                    return render_template('deck.html', username=current_user.username, deckCarte=[], error="Puoi aggiungere massimo 3 copie di una carta.")
            else:
                nuova_carta = DeckCarta(deck_id=deck.id, carta_id=carta.id, quantita=1)
                db.session.add(nuova_carta)
                db.session.commit()
            return redirect(url_for('deck'))

    deck_list = Deck.query.all()
    return render_template('deck.html', username=current_user.username, deck_list=deck_list, error=None)

@app.route('/carrello', methods=['GET', 'POST'])
@login_required
def carrello():
    # Recupera il carrello dell'utente corrente o lo crea se non esiste
    carrello = Carrello.query.filter_by(user_id=current_user.id).first()
    if not carrello:
        carrello = Carrello(user_id=current_user.id)
        db.session.add(carrello)
        db.session.commit()
    if request.method == 'POST':
        action = request.form.get('action')
        #aggiunta
        if action == 'aggCarrello':
            carta_id = request.form.get('carta_id')
            quantita = int(request.form.get('quantita', 1))
            if not carta_id or quantita < 1:
                return render_template(
                    'carrello.html', 
                    username=current_user.username, 
                    items=[], 
                    totale=0.0, 
                    error="Dati non validi."
                )
            carta = Carta.query.get(carta_id)
            if not carta:
                return render_template(
                    'carrello.html', 
                    username=current_user.username, 
                    items=[], 
                    totale=0.0, 
                    error="Carta non trovata."
                )
            carrello_item = CarrelloItem.query.filter_by(carrello_id=carrello.id, carta_id=carta.id).first()
            if carrello_item:
                carrello_item.quantita += quantita
            else:
                carrello_item = CarrelloItem(carrello_id=carrello.id, carta_id=carta.id, quantita=quantita)
                db.session.add(carrello_item)
            db.session.commit()
            return redirect(url_for('carrello'))
    items = []
    totale = 0.0
    for item in carrello.items:
        carta = item.carta
        if carta:
            totale_carta = carta.prezzo * item.quantita
            totale += totale_carta
            items.append({
                'nome': carta.nome,
                'foto': carta.foto,
                'quantita': item.quantita,
                'prezzo_unitario': carta.prezzo,
                'totale_carta': totale_carta
            })
    return render_template('carrello.html', username=current_user.username, items=items, totale=totale, error=None)

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
