# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from datetime import datetime

from werkzeug.utils import secure_filename

from PIL import Image

import os

from models  import User, Biglietto, Performance, Palco, Immagine

import utenti_dao, biglietti_dao, immagini_dao, performances_dao, palchi_dao



app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

#inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def home():
    performances = performances_dao.get_performances_pubbliche_ordinate()

    immagini_performance = {
        perf[0]: immagini_dao.get_immagini_di_performance(perf[0])
        for perf in performances
    }

    # Ricava nome e immagine dell'artista dalla stessa tabella performances
    artisti = {
        perf[0]: (perf[5], perf[7])  # nome_artista, img_artista
        for perf in performances
    }

    return render_template("home.html",
                           performances=performances,
                           immagini_performance=immagini_performance,
                           artisti=artisti)




# manda al form di login
@app.route("/login")
def login():
    return render_template("login.html")


# manda alla registrazione
@app.route("/signup")
def signup():
    return render_template("signup.html")


# manda alla pagina faq
@app.route("/faq")
def faq():
    return render_template("faq.html")


# manda alla pagina about us
@app.route("/about")
def about():
    return render_template("about.html")


# manda alla pagina biglietti
@app.route("/biglietti")
def biglietti():
    return render_template("biglietti.html")


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

    #email dal form
    email = request.form.get('txt_email')
    
    #se non è nel db flash
    if utenti_dao.get_utente_email(email):
        flash("Email già registrata!", "error")
        return redirect(url_for('signup'))
    
    #se è nel db allora prendo altri parametri e creo nuovo utente
    utenti_dao.nuovo_utente(
        request.form.get('txt_nome'),
        request.form.get('txt_cognome'),
        email,
        request.form.get('txt_password'),
        request.form.get('tipo')
    )
    
    # messaggio di ok
    flash("Registrazione completata!", "success")

    return redirect(url_for('login'))


# autentica un utente dopo il login
@app.route("/autenticare", methods=["POST"])
def autenticare_utente():

    email = request.form.get("txt_email")
    password = request.form.get("txt_password")

    utente_db = utenti_dao.get_utente_email(email)

    #se l'utente non è nel db errore e rimappo sulla home
    if not utente_db:
        
        print("Credenziali non valide")
        return redirect(url_for("home"))
        
    else:
        # creo oggetto user 
        user = User(
            id=utente_db[0],
            nome=utente_db[1],
            cognome=utente_db[2],
            email=utente_db[3],
            password=utente_db[4],
            tipo=utente_db[5],
        )

        login_user(user)

        #salvo l'utente (id + tipo)
        session['id'] = user.id
        session['tipo'] = user.tipo

        #messaggino flash
        flash("Accesso effettuato con successo!","success")

        return redirect(url_for("home"))

#route unica per il profilo
POST_IMG_WIDTH = 600  # larghezza fissa immagini

@app.route("/profilo")
@login_required
def profilo():
    tipo = session.get('tipo')

    if tipo == 'organizzatore':
        return redirect(url_for("profilo_organizzatore"))
    elif tipo == 'partecipante':
        return redirect(url_for("profilo_partecipante"))
    else:
        flash("Tipo utente non riconosciuto.", "danger")
        return redirect(url_for("home"))



#route per profilo partecipante
@app.route("/profilo_partecipante")
@login_required
def profilo_partecipante():

    # se non è un partecipante uso flash (in teoria non dovrebbe mai avere errore)
    if session.get('tipo') != 'partecipante':

        flash("Accesso non autorizzato.", "danger")

        return redirect(url_for("home"))
    
    # altrimenti prendo i biglietti dell'user corrente
    biglietti = biglietti_dao.get_biglietto_by_partecipante(current_user.id)

    return render_template("profilo_partecipante.html", biglietti=biglietti)

# profilo organizzatore
@app.route("/profilo_organizzatore", methods=["GET", "POST"])
@login_required
def profilo_organizzatore():
    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        # Estrai i dati dal form
        data = request.form.get("data")
        ora_inizio = request.form.get("ora_inizio")
        ora_fine = request.form.get("ora_fine")
        genere = request.form.get("genere")
        descrizione = request.form.get("descrizione")
        visibilita = int(request.form.get("visibilita", 0))
        id_palco = request.form.get("id_palco")
        nome_artista = request.form.get("nome_artista")
        numero_artisti = request.form.get("numero_artisti")

        # Validazione base
        if not all([data, ora_inizio, ora_fine, genere, descrizione, id_palco, nome_artista, numero_artisti]):
            flash("Errore: tutti i campi devono essere compilati.", "danger")
            return redirect(url_for("profilo_organizzatore"))

        id_palco = int(id_palco)
        numero_artisti = int(numero_artisti)

        # Verifica sovrapposizione
        if performances_dao.verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco):
            flash("Errore: performance sovrapposta a un'altra sullo stesso palco.", "danger")
            return redirect(url_for("profilo_organizzatore"))

        # Salva immagine artista
        img_artista_file = request.files.get("img_artista")
        email = current_user.email
        secondi = int(datetime.now().timestamp())

        if img_artista_file and img_artista_file.filename != "":
            img = Image.open(img_artista_file)
            ext = img_artista_file.filename.split(".")[-1]
        else:
            img = Image.open("static/images/anonimo.png")
            ext = "png"

        width, height = img.size
        new_height = int(height / width * POST_IMG_WIDTH)
        img.thumbnail((POST_IMG_WIDTH, new_height), Image.Resampling.LANCZOS)

        filename_artista = f"@{email.lower()}-{secondi}_artista.{ext}"
        path_artista = os.path.join("static", "images", filename_artista)
        img.save(path_artista)
        img_artista_url = os.path.join("static", "images", filename_artista)

        # Inserisci performance
        id_perf = performances_dao.nuova_performance(
            data, ora_inizio, ora_fine, descrizione,
            nome_artista, numero_artisti, img_artista_url,
            genere, visibilita, id_palco, current_user.id
        )

        # Immagini della performance
        performance_imgs = request.files.getlist("img_performance[]")
        for i, file in enumerate(performance_imgs):
            if file and file.filename != "":
                img = Image.open(file)
                ext = file.filename.split(".")[-1]
                img.thumbnail((POST_IMG_WIDTH, new_height), Image.Resampling.LANCZOS)
                filename_perf = f"@{email.lower()}-{secondi}_performance_{i}.{ext}"
                path_perf = os.path.join("static", "images", filename_perf)
                img.save(path_perf)

                img_url = os.path.join("static", "images", filename_perf)
                immagini_dao.aggiungi_immagine_performance(id_perf, img_url)

        flash("Performance creata con successo!", "success")
        return redirect(url_for("profilo_organizzatore"))

    # GET request
    pubblicate = performances_dao.get_performances_pubbliche_organizzatore(current_user.id)
    bozze = performances_dao.get_bozze_organizzatore(current_user.id)
    palchi = palchi_dao.get_palchi()

    immagini_performance = {
        perf[0]: immagini_dao.get_immagini_di_performance(perf[0]) for perf in pubblicate
    }

    artisti = {
        perf[0]: (perf[5], perf[6]) for perf in pubblicate  # nome_artista, img_artista
    }

    return render_template(
        "profilo_organizzatore.html",
        pubblicate=pubblicate,
        bozze=bozze,
        palchi=palchi,
        immagini_performance=immagini_performance,
        artisti=artisti
    )

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