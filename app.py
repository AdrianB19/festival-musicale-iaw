# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import os

from models  import User, Biglietto, Performance, Palco
import utenti_dao, biglietti_dao, performances_dao, palchi_dao 

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

#inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
POST_IMG_WIDTH = 600

@app.route('/')
def home():
    #prendo le performances
    performances = performances_dao.get_performances_pubbliche()
    #dalle perforances faccio un dizionario con id - nome artista ed url_immagine
    
    artisti = {
    perf[0]: (perf[5], perf[6])
    for perf in performances
    }
    return render_template("home.html",
                          performances=performances,
                          artisti=artisti)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/biglietti")
def biglietti():
    return render_template("biglietti2.html")

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

    if session.get('tipo') != 'partecipante':

        flash("Accesso non autorizzato.", "danger")

        return redirect(url_for("home"))
    
    # altrimenti prendo i biglietti dell'user corrente
    biglietti = biglietti_dao.get_biglietto_by_partecipante(current_user.id)

    return render_template("profilo_partecipante.html", biglietti=biglietti)

@app.route("/profilo_organizzatore", methods=["GET", "POST"])
@login_required
def profilo_organizzatore():

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for("home"))
    
    pubblicate = performances_dao.get_performances_pubbliche_organizzatore(current_user.id)
    bozze = performances_dao.get_bozze_organizzatore(current_user.id)
    palchi = palchi_dao.get_palchi()

    artisti = {
        perf[0]: (perf[5], perf[6]) for perf in pubblicate + bozze
    }

    return render_template(
        "profilo_organizzatore.html",
        pubblicate=pubblicate,
        bozze=bozze,
        palchi=palchi,
        artisti=artisti
    )

@app.route("/nuova_performance", methods=["POST"])
@login_required
def nuova_performance():
    #campi dal form
    data = request.form.get("data")
    ora_inizio = request.form.get("ora_inizio")
    ora_fine = request.form.get("ora_fine")
    genere = request.form.get("genere")
    descrizione = request.form.get("descrizione")
    visibilita = int(request.form.get("visibilita"))
    id_palco = int(request.form.get("id_palco"))
    nome_artista = request.form.get("nome_artista")
    uploaded_file = request.files["img_artista"]

    # Validazione campi
    if not all([data, ora_inizio, ora_fine, genere, descrizione, id_palco, nome_artista]):
        flash("Errore: tutti i campi devono essere compilati.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if performances_dao.artista_esiste(nome_artista):
        flash("Errore: esiste già una performance con questo nome artista.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    # Conversione in datetime 
    inizio_dt = datetime.strptime(ora_inizio, "%H:%M")
    fine_dt = datetime.strptime(ora_fine, "%H:%M")

    # Se fine è prima di inizio, considera che passa la mezzanotte
    if fine_dt <= inizio_dt:
        flash("L'ora di inizio deve essere precedente all'ora di fine.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    # Controllo che inizio sia dopo le 14:00
    if inizio_dt.time() < datetime.strptime("14:00", "%H:%M").time():
        flash("L'ora di inizio deve essere dopo le 14:00.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    # Controllo durata massima
    durata = fine_dt - inizio_dt
    if durata > timedelta(hours=1, minutes=30):
        flash("La performance non deve durare più di 90 minuti.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    if visibilita == 1:
        if performances_dao.verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco):
            flash("Errore: performance sovrapposta a un'altra sullo stesso palco.", "danger")
            return redirect(url_for("profilo_organizzatore"))

    img = Image.open(uploaded_file)
    ext = uploaded_file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        flash("Errore: solo immagini PNG o JPG sono accettate.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    width, height = img.size
    new_height = height /width *POST_IMG_WIDTH
    size = POST_IMG_WIDTH, new_height
    img.thumbnail(size, Image.Resampling.LANCZOS)
    secondi = int(datetime.now().timestamp())
    safe_nome_artista = nome_artista.lower().replace(" ", "_")
    img.save(f"static/images/@{safe_nome_artista}-{secondi}.{ext}")
    nuovo_nome_foto = f"images/@{safe_nome_artista}-{secondi}.{ext}"

    performances_dao.nuova_performance(
        data, ora_inizio, ora_fine, descrizione,
        nome_artista, nuovo_nome_foto,
        genere, visibilita, id_palco, current_user.id
    )

    flash("Performance creata con successo!", "success")
    return redirect(url_for("profilo_organizzatore"))

@app.route("/pubblica_bozza/<int:id>", methods=["POST"])
@login_required
def pubblica_bozza(id):
    bozza = performances_dao.get_performance_by_id(id)

    if not bozza:
        flash("Bozza non trovata.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    data = bozza["data"]
    ora_inizio = bozza["ora_inizio"]
    ora_fine = bozza["ora_fine"]
    id_palco = bozza["id_palco"]
    nome_artista = bozza["nome_artista"]

    # Controllo sovrapposizione
    sovrapposte = performances_dao.verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco)
    if sovrapposte:
        flash("Errore: la performance si sovrappone a un'altra già pubblicata sullo stesso palco.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    performances_dao.pubblica_performance(id)
    flash("Bozza pubblicata con successo!", "success")
    return redirect(url_for("profilo_organizzatore"))

@app.route("/modifica_bozza/<int:id>", methods=["GET", "POST"])
@login_required
def modifica_bozza(id):
    bozza = performances_dao.get_performance_by_id(id)

    if not bozza:
        flash("Bozza non trovata", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    # dati dal form
    data = request.form.get("data")
    ora_inizio = request.form.get("ora_inizio")
    ora_fine = request.form.get("ora_fine")
    genere = request.form.get("genere")
    descrizione = request.form.get("descrizione")
    visibilita = 0
    id_palco = int(request.form.get("id_palco"))
    nome_artista = request.form.get("nome_artista")
    uploaded_file = request.files.get("img_artista")

    if not all([data, ora_inizio, ora_fine, genere, descrizione, id_palco, nome_artista]):
        flash("Errore: tutti i campi devono essere compilati.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    # Controlli base: ora inizio < ora fine && ora inizio >= 14:00
    inizio_dt = datetime.strptime(ora_inizio, "%H:%M")
    fine_dt = datetime.strptime(ora_fine, "%H:%M")

    if fine_dt <= inizio_dt:
        flash("L'ora di inizio deve essere precedente all'ora di fine.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if inizio_dt.time() < datetime.strptime("14:00", "%H:%M").time():
        flash("L'ora di inizio deve essere dopo le 14:00.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if (fine_dt - inizio_dt) > timedelta(minutes=90):
        flash("La performance non deve durare più di 90 minuti.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    # Gestione immagine
    if uploaded_file and uploaded_file.filename != "":
        ext = uploaded_file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            flash("Errore: solo immagini PNG o JPG sono accettate.", "danger")
            return redirect(url_for("profilo_organizzatore"))

        img = Image.open(uploaded_file)
        width, height = img.size
        new_height = height / width * POST_IMG_WIDTH
        img.thumbnail((POST_IMG_WIDTH, new_height), Image.Resampling.LANCZOS)
        timestamp = int(datetime.now().timestamp())
        safe_nome = nome_artista.lower().replace(" ", "_")
        path_salvato = f"static/images/@{safe_nome}-{timestamp}.{ext}"
        img.save(path_salvato)
        img_artista_url = f"images/@{safe_nome}-{timestamp}.{ext}"
    else:
        img_artista_url = bozza["img_artista"]

    performances_dao.aggiorna_bozza(
        id, data, ora_inizio, ora_fine, descrizione,
        nome_artista, img_artista_url, genere, visibilita, id_palco
    )

    flash("Bozza aggiornata con successo!", "success")
    return redirect(url_for("profilo_organizzatore"))


@app.route("/acquista_biglietto", methods=["POST"])
@login_required
def acquista_biglietto():
    #prendo i campi dal form
    if session.get('tipo') != 'partecipante':
        flash("Errore: sei un organizzatore, non puoi comprare un biglietto", "danger")
        return redirect(url_for("biglietti"))
    
    start_date = request.form("start_date")
    tipo = request.form("tipo")
    id_utente = current_user.id

    if not all([start_date, tipo, id_utente]):
        flash("Errore: tutti i campi devono essere compilati.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    #verifica che l'utente non abbia già acquistato un biglietto
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