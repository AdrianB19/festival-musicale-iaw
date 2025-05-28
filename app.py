# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash

from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from models  import User, Biglietto, Artista, Performance, Palco, Immagine

import utenti_dao, biglietti_dao, artisti_dao, immagini_dao, performances_dao

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

#inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

# manda alla home
@app.route("/")
def home():
    return render_template("home.html")

# manda al form di login
@app.route("/login")
def login():
    return render_template("login.html")

# manda alla registrazione
@app.route("/signup")
def signup():
    return render_template("signup.html")

# manda alla pagina about us
@app.route("/faq")
def faq():
    return render_template("faq.html")

# manda alla pagina about us
@app.route("/about")
def about():
    return render_template("about.html")

# disconnette l'utente autenticato, protetto con login_required
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sei stato disconnesso", "info")
    return redirect(url_for("home"))

# gestisce registrazione con controlli inclusi su esistenza
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

# autentica un utente dopo il login
@app.route("/autenticare", methods=["POST"])
def autenticare_utente():
    email = request.form.get("txt_email")
    password = request.form.get("txt_password")

    utente_db = utenti_dao.get_utente_email(email)

    if not utente_db:
        
        print("Credenziali non valide")
        return redirect(url_for("home"))
    
        #verifica sul controllo della password
        
    else:
        user = User(
            id=utente_db[0],
            nome=utente_db[1],
            cognome=utente_db[2],
            email=utente_db[3],
            password=utente_db[4],
            tipo=utente_db[5],
        )

        login_user(user)

        flash("Accesso effettuato con successo!","success")
        return redirect(url_for("home"))


# carica utente dal db in base al suo id
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