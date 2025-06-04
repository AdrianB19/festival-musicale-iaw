# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import os

from models  import User, Biglietto, Performance, Palco
import utenti_dao, biglietti_dao, performances_dao, palchi_dao , acquisti_dao

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

#inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}  # formati di foto accettabili
POST_IMG_WIDTH = 600 # profondità immagini

# pagina di inizio
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

# form per il login che ti fa accedere salvando id, tipo utente
@app.route("/login")
def login():
    return render_template("login.html")

# form di iscrizione che poi andrà su nuovo_utente
@app.route("/signup")
def signup():
    return render_template("signup.html")

# pagina standalone
@app.route("/faq")
def faq():
    return render_template("faq.html")

# pagina standalone
@app.route("/about")
def about():
    return render_template("about.html")

# passo biglietti + stats
@app.route("/biglietti")
def biglietti():
    dati_biglietti = biglietti_dao.get_opzioni_biglietti()
    statistiche_disponibilita = acquisti_dao.get_statistiche_disponibilita()
    return render_template("biglietti.html", dati_biglietti = dati_biglietti, statistiche_disponibilita=statistiche_disponibilita)

# disconnette utente e cancella dalla sessione i dati (tipo ed id)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('tipo', None)  
    flash("Sei stato disconnesso", "info")
    return redirect(url_for("home"))

# gestisce registrazione con controlli inclusi su esistenza
@app.route("/subscribe", methods=["POST"])
def subscribe():

    email = request.form.get('txt_email') # prendo email da form
    
    #se è già nel db non può usarla per registrarsi
    if utenti_dao.get_utente_email(email):
        flash("Email già registrata!", "error")
        return redirect(url_for('signup'))
    
    #se non è nel db prendo altri campi e iniserisco un nuovo utente nel db
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
        abort(404)

#route per profilo partecipante
@app.route("/profilo_partecipante", methods = ["GET", "POST"])
@login_required
def profilo_partecipante():

    if session.get('tipo') != 'partecipante':
        flash("Accesso non autorizzato.", "danger")
        abort(404)
    
    # vedo se un utente ha un comprato un biglietto, lo prendo dal db e passo anche data acquisto

    id_biglietto = acquisti_dao.verifica_acquisto_utente(current_user.id)
    
    if id_biglietto is not None:

        biglietto = biglietti_dao.get_biglietto(id_biglietto)
        data, orario = acquisti_dao.get_data_acquisto(current_user.id)
        
    else:
        biglietto = None
        data, orario = None

    return render_template("profilo_partecipante.html", biglietto=biglietto, data=data, orario = orario)

# route per il profilo organizzatore, deve caricare perf pubblicate e bozze
@app.route("/profilo_organizzatore", methods=["GET", "POST"])
@login_required
def profilo_organizzatore():

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(404)
    
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

# creo una nuova performance e leggo dati dal form
@app.route("/nuova_performance", methods=["POST"])
@login_required
def nuova_performance():

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(404)

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

    # il nome artista è univoco
    if performances_dao.artista_esiste(nome_artista):
        flash("Errore: esiste già una performance con questo nome artista.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    # converto in datetime 
    inizio_dt = datetime.strptime(ora_inizio, "%H:%M")
    fine_dt = datetime.strptime(ora_fine, "%H:%M")

    # se fine è prima di inizio, considera che passa la mezzanotte
    if fine_dt <= inizio_dt:
        flash("L'ora di inizio deve essere precedente all'ora di fine.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    # controllo che inizio sia dopo le 14:00
    if inizio_dt.time() < datetime.strptime("14:00", "%H:%M").time():
        flash("L'ora di inizio deve essere dopo le 14:00.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    # durata massima non oltre 1.30 h
    durata = fine_dt - inizio_dt
    if durata > timedelta(hours=1, minutes=30):
        flash("La performance non deve durare più di 90 minuti.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    # se deve esser pubblicata subito
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

# pubblica una bozza e verifica sovrapposizione / durata max
@app.route("/pubblica_bozza/<int:id>", methods=["POST"])
@login_required
def pubblica_bozza(id):

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(404)

    bozza = performances_dao.get_performance_by_id(id)

    if not bozza:
        flash("Bozza non trovata.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    data = bozza["data"]
    ora_inizio = bozza["ora_inizio"]
    ora_fine = bozza["ora_fine"]
    id_palco = bozza["id_palco"]
    nome_artista = bozza["nome_artista"]

    # controllo sovrapposizione
    sovrapposte = performances_dao.verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco)
    if sovrapposte:
        flash("Errore: la performance si sovrappone a un'altra già pubblicata sullo stesso palco.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    performances_dao.pubblica_performance(id)
    flash("Bozza pubblicata con successo!", "success")
    return redirect(url_for("profilo_organizzatore"))

# modifica la bozza
@app.route("/modifica_bozza/<int:id>", methods=["GET", "POST"])
@login_required
def modifica_bozza(id):

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(404)

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

# acquisto un biglietto verificando che non ne abbia già acquistato uno, che ci sia disponibilita
@app.route("/acquista_biglietto", methods=["POST"])
@login_required
def acquista_biglietto():
    # verifica tipo utente
    if session.get('tipo') != 'partecipante':
        flash("Errore: sei un organizzatore, non puoi comprare un biglietto", "danger")
        abort(404)
    
    # recupera dati dal form
    start_date = request.form.get("start_date", "").strip()
    tipo = request.form.get("tipo", "").strip()
    id_utente = current_user.id
    
    #  campi obbligatori anche se è una selezione
    if not all([start_date, tipo, id_utente]):
        flash("Errore: tutti i campi devono essere compilati.", "danger")
        return redirect(url_for("biglietti"))
    
    # verifica se ha già un biglietto
    if acquisti_dao.verifica_acquisto_utente(id_utente):
        flash("Hai già acquistato un biglietto!", "danger")
        return redirect(url_for("profilo_partecipante"))
    
    # per semplificare la query
    single_day = None
    double_first = None
    double_second = None
    
    try:
        if tipo == 'Giornaliero':
            single_day = start_date
        elif tipo == 'Due giorni':
            giorni = start_date.split(",")
            if len(giorni) != 2:
                raise ValueError("Formato date non valido per Due Giorni")
            double_first, double_second = [g.strip() for g in giorni]
        elif tipo != 'Full pass':
            flash("Tipo biglietto non valido!", "danger")
            return redirect(url_for("biglietti"))
    except ValueError as e:
        flash(f"Errore nei dati inseriti: {str(e)}", "danger")
        return redirect(url_for("biglietti"))
    
    # NUOVO: Verifica disponibilità biglietti
    disponibilita = acquisti_dao.verifica_disponibilita_biglietto(
        tipo, single_day, double_first, double_second
    )
    
    # dispobibilita nei giorni
    if not disponibilita['disponibile']:
        flash(f"Biglietto non disponibile: {disponibilita['messaggio']}", "danger")
        return redirect(url_for("biglietti"))
    
    # data corrente yyyy-mm-dd hh:mm
    data_acquisto = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # id biglietto
    try:
        biglietto = biglietti_dao.get_id_biglietto(tipo, single_day, double_first, double_second)
        
        # Gestione caso nessun risultato trovato
        if not biglietto:
            flash("Biglietto non disponibile per le date selezionate", "danger")
            return redirect(url_for("biglietti"))
        
        # ID biglietto dal risultato è una tupla (id,)
        id_biglietto = biglietto[0] if isinstance(biglietto, tuple) else biglietto
        
    except Exception as e:
        print(f"Errore nel recupero ID biglietto: {e}")
        flash("Errore nel recuperare i dati del biglietto", "danger")
        return redirect(url_for("biglietti"))
    
    # acquisto
    try:
        acquisti_dao.nuovo_acquisto(id_utente, id_biglietto, data_acquisto)
        flash("Acquisto completato con successo!", "success")
        return redirect(url_for("profilo_partecipante"))
    except Exception as e:
        print(f"Errore durante l'acquisto: {e}")
        flash("Errore durante l'acquisto", "danger")
        return redirect(url_for("biglietti"))

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