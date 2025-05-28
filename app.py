# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash

from flask_login import LoginManager, login_user, login_required, current_user

from models  import User, Biglietto, Artista, Performance, Palco, Immagine

import utenti_dao, biglietti_dao, artisti_dao, immagini_dao, performances_dao

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

#inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

#processo i dati del form
@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get('txt_email')
    
    if utenti_dao.get_utente_email(email):
        flash("Email già registrata!", "error")
        return redirect(url_for('signup'))
    
    utenti_dao.nuovo_utente(
        request.form.get('txt_nome'),
        request.form.get('txt_cognome'),
        email,
        request.form.get('txt_password'),
        request.form.get('tipo')
    )
    
    flash("Registrazione completata!", "success")
    return redirect(url_for('login'))

@app.route("/autenticare", methods=["POST"])
def autenticare_utente():

    #funzione vera e propria a cui punto dopo aver fatto il login

    utente_form = request.form.to_dict()  
    utente_db = utenti_dao.get_user_by_email(utente_form["txt_email"])
    #query per email

    if not utente_db:
        
        print("Credenziali non valide")
        return redirect(url_for("home"))
    
        #verifica sul controllo della password
        
    else:
        new = User(
            id=utente_db["id"],
            nome=utente_db["nome"],
            cognome=utente_db["cognome"],
            email=utente_db["email"],
            password=utente_db["password"],
        )

        login_user(new)

        return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    user_data = utenti_dao.get_utente_id(user_id)
    if user_data:
        return User(
            id=user_data[0], 
            nome=user_data[1], 
            cognome=user_data[2],
            email=user_data[3],
            password=user_data[4],
            tipo=user_data[5]
        )
    return None