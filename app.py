# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import os

from models  import User
import utenti_dao, biglietti_dao, performances_dao, palchi_dao , acquisti_dao, immagini_dao

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

# inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "SVG", "WebP", "webp", "avif"}
UPLOAD_FOLDER = 'static/images/'

@app.route('/')
def home():
    # Recupero i filtri dalla query string
    palco_id = request.args.get('palco')
    data = request.args.get('data')
    genere = request.args.get('genere')
    
    # Se ci sono filtri, uso la funzione filtrata, altrimenti quella standard
    if palco_id or data or genere:
        performances = performances_dao.get_performances_filtrate(
            palco_id=palco_id,
            data=data,
            genere=genere
        )
    else:
        performances = performances_dao.get_performances_pubbliche()
    
    # Creo il dizionario degli artisti
    artisti = {
        perf[0]: (perf[5], perf[6])
        for perf in performances
    }
    
    # Recupero le opzioni per i filtri
    palchi_disponibili = palchi_dao.get_palchi()
    date_disponibili = performances_dao.get_date_disponibili()
    generi_disponibili = performances_dao.get_generi_disponibili()
    
    return render_template("home.html",
                          performances=performances,
                          artisti=artisti,
                          palchi_disponibili=palchi_disponibili,
                          date_disponibili=date_disponibili,
                          generi_disponibili=generi_disponibili,
                          filtro_palco=palco_id,
                          filtro_data=data,
                          filtro_genere=genere)

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
    
    password = request.form.get('txt_password')
    if len(password) < 8:
        flash("La password deve contenere almeno 8 caratteri.", "error")
        return redirect(url_for('signup'))

    hashed_password = generate_password_hash(password)
    
    #se non è nel db prendo altri campi e iniserisco un nuovo utente nel db
    utenti_dao.nuovo_utente(
        request.form.get('txt_nome'),
        request.form.get('txt_cognome'),
        email,
        hashed_password,
        request.form.get('tipo')
    )
    
    flash("Registrazione completata!", "success")

    return redirect(url_for('login'))

# autenticazione login
@app.route("/autenticare", methods=["POST"])
def autenticare_utente():
    email = request.form.get("txt_email")
    password = request.form.get("txt_password")

    utente_db = utenti_dao.get_utente_email(email)

    if not utente_db:
        flash("Credenziali non valide", "danger")
        return redirect(url_for("login"))

    # utente_db[4] è la password hashata salvata nel DB
    if not check_password_hash(utente_db[4], password):
        flash("Credenziali non valide", "danger")
        return redirect(url_for("login"))

    # Se la password è corretta, prosegui con il login
    user = User(
        id=utente_db[0],
        nome=utente_db[1],
        cognome=utente_db[2],
        email=utente_db[3],
        password=utente_db[4],  # hash nel DB (ok)
        tipo=utente_db[5],
    )

    login_user(user)
    session['id'] = user.id
    session['tipo'] = user.tipo

    flash("Accesso effettuato con successo!", "success")
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
        data = ""
        orario = ""

    return render_template("profilo_partecipante.html", biglietto=biglietto, data=data, orario = orario)

@app.route("/profilo_organizzatore", methods=["GET", "POST"])
@login_required
def profilo_organizzatore():
    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(404)

    palco_id = request.args.get('palco')
    data = request.args.get('data')
    genere = request.args.get('genere')

    pubblicate = performances_dao.get_performances_filtrate(palco_id, data, genere)
    bozze = performances_dao.get_bozze_organizzatore(current_user.id)
    
    palchi = palchi_dao.get_palchi()
    date = performances_dao.get_date_disponibili()
    generi = performances_dao.get_generi_disponibili()

    artisti = {
        perf[0]: (perf[5], perf[6]) for perf in pubblicate + bozze
    }

    statistiche_disponibilita = acquisti_dao.get_statistiche_disponibilita()

    return render_template(
        "profilo_organizzatore.html",
        pubblicate=pubblicate,
        bozze=bozze,
        palchi=palchi,
        date=date,
        generi=generi,
        filtro_palco=palco_id,
        filtro_data=data,
        filtro_genere=genere,
        artisti=artisti,
        statistiche_disponibilita=statistiche_disponibilita
    )

# creo una nuova performance e leggo dati dal form
@app.route("/nuova_performance", methods=["POST"])
@login_required
def nuova_performance():
    if session.get('tipo') != 'organizzatore':
        flash("Accesso proibito.", "danger")
        abort(403)

    # campi form
    data = request.form.get("data")
    ora_inizio = request.form.get("ora_inizio")
    ora_fine = request.form.get("ora_fine")
    genere = request.form.get("genere")
    descrizione = request.form.get("descrizione")
    visibilita = int(request.form.get("visibilita"))
    id_palco = int(request.form.get("id_palco"))
    nome_artista = request.form.get("nome_artista")
    uploaded_file = request.files["img_artista"]

    # validazioen
    if not all([data, ora_inizio, ora_fine, genere, descrizione, id_palco, nome_artista]):
        flash("Errore: tutti i campi devono essere compilati.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if performances_dao.artista_esiste(nome_artista):
        flash("Errore: esiste già una performance con questo nome artista.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    try:
        inizio_dt = datetime.strptime(ora_inizio, "%H:%M")
        fine_dt = datetime.strptime(ora_fine, "%H:%M")
    except ValueError:
        flash("Formato orario non valido.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if fine_dt <= inizio_dt:
        flash("L'ora di inizio deve essere precedente all'ora di fine.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if inizio_dt.time() < datetime.strptime("14:00", "%H:%M").time():
        flash("L'ora di inizio deve essere dopo le 14:00.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if (fine_dt - inizio_dt) > timedelta(hours=1, minutes=30):
        flash("La performance non deve durare più di 90 minuti.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    if visibilita == 1:
        if performances_dao.verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco):
            flash("Errore: performance sovrapposta a un'altra sullo stesso palco.", "danger")
            return redirect(url_for("profilo_organizzatore"))

    nuovo_nome_foto = salva_immagine(uploaded_file, nome_artista)
    if not nuovo_nome_foto:
        flash("Errore: solo immagini PNG, JPG, JPEG, SVG o WebP sono accettate.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    # crea perf
    performances_dao.nuova_performance(
        data, ora_inizio, ora_fine, descrizione,
        nome_artista, nuovo_nome_foto,
        genere, visibilita, id_palco, current_user.id
    )

    id = performances_dao.get_id_by_artista(nome_artista)

    # processo per le immagini del carousel
    for i in range(1, 6):  
        file = request.files.get(f'foto{i}')
        if file and file.filename != '':
            carousel_url = salva_immagine(file, nome_artista, "carousel_", i)
            if carousel_url:
                image_url = f'/static/{carousel_url}'
                immagini_dao.insert_immagine(id, image_url)

    flash("Performance creata con successo!", "success")
    return redirect(url_for("profilo_organizzatore"))

@app.route('/performance/<int:id>')
def dettaglio_performance(id):

    performance = performances_dao.get_performance_by_id(id)

    immagini = immagini_dao.get_immagini_by_id_perf(id)

    durata = (int(performance['ora_fine'][:2]) - int(performance['ora_inizio'][:2])) * 60 + \
             (int(performance['ora_fine'][3:5]) - int(performance['ora_inizio'][3:5]))

    return render_template('dettaglio_performance.html', performance=performance, immagini=immagini, durata=durata)

# pubblica una bozza e verifica sovrapposizione / durata max
@app.route("/pubblica_bozza/<int:id>", methods=["POST"])
@login_required
def pubblica_bozza(id):

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(404)

    bozza = performances_dao.get_bozza_by_id(id)

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

# acquisto un biglietto verificando che non ne abbia g# modifica la bozza
@app.route("/modifica_bozza/<int:id>", methods=["GET", "POST"])
@login_required
def modifica_bozza(id):

    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        abort(403)

    bozza = performances_dao.get_bozza_by_id(id)
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

    # validazione 
    if not all([data, ora_inizio, ora_fine, genere, descrizione, id_palco, nome_artista]):
        flash("Errore: tutti i campi devono essere compilati.", "danger")
        return redirect(url_for("profilo_organizzatore"))
    
    try:
        inizio_dt = datetime.strptime(ora_inizio, "%H:%M")
        fine_dt = datetime.strptime(ora_fine, "%H:%M")
    except ValueError:
        flash("Formato orario non valido.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if fine_dt <= inizio_dt:
        flash("L'ora di inizio deve essere precedente all'ora di fine.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if inizio_dt.time() < datetime.strptime("14:00", "%H:%M").time():
        flash("L'ora di inizio deve essere dopo le 14:00.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if (fine_dt - inizio_dt) > timedelta(minutes=90):
        flash("La performance non deve durare più di 90 minuti.", "danger")
        return redirect(url_for("profilo_organizzatore"))

    if uploaded_file and uploaded_file.filename != "":
        img_artista_url = salva_immagine(uploaded_file, nome_artista)
        if not img_artista_url:
            flash("Errore: solo immagini PNG, JPG, JPEG, SVG o WebP sono accettate.", "danger")
            return redirect(url_for("profilo_organizzatore"))
    else:
        img_artista_url = bozza["img_artista"]

    performances_dao.aggiorna_bozza(
        id, data, ora_inizio, ora_fine, descrizione,
        nome_artista, img_artista_url, genere, visibilita, id_palco
    )

    immagini_esistenti = immagini_dao.get_immagini_by_id_perf(id)

    for i in range(1, 6):
        file = request.files.get(f'foto{i}')
        if file and file.filename != '':
            carousel_url = salva_immagine(file, nome_artista, "carousel_", i)
            if carousel_url:
                nuovo_url = f"/static/{carousel_url}"

                if i <= len(immagini_esistenti):
                    vecchio_url = immagini_esistenti[i - 1]
                    immagini_dao.update_immagine_perf(id, vecchio_url, nuovo_url)

                    # Rimuovi vecchia immagine se esiste
                    vecchio_path = vecchio_url.lstrip("/")
                    if os.path.exists(vecchio_path):
                        os.remove(vecchio_path)
                else:
                    immagini_dao.insert_immagine(id, nuovo_url)

    flash("Bozza aggiornata con successo!", "success")
    return redirect(url_for("profilo_organizzatore"))

@app.route("/elimina_performance/<int:id>", methods=["POST"])
@login_required
def elimina_performance(id):

    if session.get('tipo') != 'organizzatore':
        abort(403)
    immagini_dao.delete_immagini_performance(id)
    performances_dao.elimina_performance(id)
    flash("Performance eliminata.", "success")
    return redirect(url_for("profilo_organizzatore"))

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
    

    if tipo == 'Giornaliero':
        single_day = start_date
    elif tipo == 'Due giorni':
        try:
            giorni = start_date.split(",")
            if len(giorni) != 2:
                raise ValueError("Formato date non valido per Due Giorni")
            double_first, double_second = [g.strip() for g in giorni]
        except ValueError as e:
            flash("Formato date non valido per biglietto Due Giorni", "danger")
            return redirect(url_for("biglietti"))
    elif tipo != 'Full pass':
        flash("Tipo biglietto non valido!", "danger")
        return redirect(url_for("biglietti"))

    
    # verifico la disponibilità biglietti
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
    

    acquisti_dao.nuovo_acquisto(id_utente, id_biglietto, data_acquisto)
    flash("Acquisto completato con successo!", "success")
    return redirect(url_for("profilo_partecipante"))

def salva_immagine(file, nome_artista, prefisso="", numero=None):
    if not file or file.filename == "":
        return None

    # controllo estensione
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None

    try:
        # l'immagine con PIL
        img = Image.open(file)

        # nuova altezza mantenendo il rapporto d'aspetto
        width, height = img.size
        new_height = int(height / width * POST_IMG_WIDTH)
        size = (POST_IMG_WIDTH, new_height)

        # ridimensiona l'immagine
        img.thumbnail(size, Image.Resampling.LANCZOS)

        #  nome sicuro per il file
        safe_nome = nome_artista.lower().replace(" ", "_")
        timestamp = int(datetime.now().timestamp())

        if numero:
            filename = f"{prefisso}{safe_nome}_{numero}_{timestamp}.{ext}"
        else:
            filename = f"{prefisso}{safe_nome}_{timestamp}.{ext}"

        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # salvo l'immagine nella cartella static/images/
        img.save(file_path)

        # path relativo per usarlo nell'app
        return f"images/{filename}"
    
    except Exception as e:
        print(f"Errore nel processare l'immagine: {e}")
        return None


# carica utente dal db in base al suo id
@login_manager.user_loader
def load_user(user_id):

    try:
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
    except Exception as e:
        print(f"Errore nel caricare l'utente {user_id}: {e}")
        return None
