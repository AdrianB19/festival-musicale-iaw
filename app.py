# import necessari a visualizzazione delle routes, per l'autenticazione, per vedere i moduli
from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from models  import User, Biglietto, Artista, Performance, Palco, Immagine

import utenti_dao, biglietti_dao, artisti_dao, immagini_dao, performances_dao, palchi_dao

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

#inizializzazione del login manager
login_manager = LoginManager()
login_manager.init_app(app)

# manda alla home
@app.route("/")
def home():
    performances = performances_dao.get_performance_pubbliche()
    return render_template("home.html", performances=performances)

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

        #salvo l'utente (id + tipo)
        session['id'] = user.id
        session['tipo'] = user.tipo

        flash("Accesso effettuato con successo!","success")
        return redirect(url_for("home"))

#route unica per il profilo
@app.route('/profilo', methods=['GET', 'POST'])
@login_required
def profilo():
    if session.get('tipo') == 'organizzatore':
        if request.method == 'POST':
            # gestione form (come fatto prima)
            ...

        pubblicate = performances_dao.get_performance_pubblicate_by_organizzatore(current_user.id)
        bozze = performances_dao.get_bozze_by_organizzatore(current_user.id)
        palchi = palchi_dao.get_palchi()

        # immagini performance
        immagini_performance = {}
        for perf in pubblicate:
            img_ids = immagini_dao.get_immagini_di_performance(perf[0])
            immagini_performance[perf[0]] = img_ids  # img_ids è lista di tuple (id_img,)

        # artista: supponiamo che artista (nome, foto) sia associato alla performance in modo 1:1
        artisti = {}
        for perf in pubblicate:
            artista_info = artisti_dao.get_artista_by_performance(perf[0])  # tu devi implementare questa funzione
            artisti[perf[0]] = artista_info  # es. ("Coldplay", "foto.jpg")

        return render_template("profilo_organizzatore.html", pubblicate=pubblicate, bozze=bozze,
                               palchi=palchi, immagini_performance=immagini_performance, artisti=artisti)





#route per profilo partecipante
@app.route("/profilo_partecipante")
@login_required
def profilo_partecipante():
    if session.get('tipo') != 'partecipante':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for("home"))
    
    biglietti = biglietti_dao.get_biglietti_by_utente(current_user.id)
    return render_template("profilo_partecipante.html", biglietti=biglietti)

# profilo organizzatore
@app.route("/profilo_organizzatore", methods=["GET", "POST"])
@login_required
def profilo_organizzatore():
    if session.get('tipo') != 'organizzatore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for("home"))
    
    if request.method == "POST":
        # Recupera i dati dal form
        data = request.form.get("data")
        ora_inizio = request.form.get("ora_inizio")
        durata = request.form.get("durata")
        genere = request.form.get("genere")
        descrizione = request.form.get("descrizione")
        visibilita = int(request.form.get("visibilita"))
        id_palco = int(request.form.get("id_palco"))
        
        # Calcola ora_fine
        from datetime import datetime, timedelta
        ora_inizio_dt = datetime.strptime(ora_inizio, "%H:%M")
        ora_fine_dt = ora_inizio_dt + timedelta(minutes=int(durata))
        ora_fine = ora_fine_dt.strftime("%H:%M")
        
        # Verifica sovrapposizione
        sovrapposta = performances_dao.verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco)
        if sovrapposta:
            flash("Errore: la performance si sovrappone a un'altra già pubblicata su questo palco.", "danger")
        else:
            performances_dao.nuova_performance(data, ora_inizio, durata, genere, descrizione, visibilita, id_palco, current_user.id)
            flash("Performance aggiunta con successo.", "success")
            return redirect(url_for("profilo_organizzatore"))
    
    # Recupera le performance e i palchi
    performance_pubblicate = performances_dao.get_performance_pubblicate_by_organizzatore(current_user.id)
    bozze = performances_dao.get_bozze_by_organizzatore(current_user.id)
    palchi = palchi_dao.get_palchi()
    
    return render_template("profilo_organizzatore.html", performance_pubblicate=performance_pubblicate, bozze=bozze, palchi=palchi)

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