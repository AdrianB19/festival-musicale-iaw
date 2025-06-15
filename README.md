# festival-musicale-iaw

Progetto d’esame per il corso **Introduzione alle Applicazioni Web** presso il Politecnico di Torino (Giugno 2025).

---

## Istruzioni sulla navigazione
Per quanto riguarda la navigazione del sito, sono state introdotte una pagina About Us ed una pagina FAQs.
<br>La pagina Acquisti, valevole per l'acquisto di un biglietto e contenente le statistiche sulle disponibilità è visibile solamente per gli utenti di tipo partecipante.
<br>La pagina profilo organizzatore contiene tutte le performance con opzioni di filtraggio, una sezione per le proprie bozze, la possibilità di creare una nuova performance e le statistiche sulle vendite dei biglietti.
<br>Le performance sono visibili nella home, cliccando su di esse la si vede in modo esteso con un carousel contenente le eventuali immagini opzionali + quella dell'artista

### Gestione delle performance
Per quanto riguarda la gestione della performance (lato organizzatore) , queste sono inseribili direttamente dal profilo organizzatore. Una performance può avere fino a 5 immagini promozionali opzionali mentre è obbligatorio inserire un'immagine dell'artista.<br>
Una performance con **visibilità pubblica** verrà validata se: 
<p>
- non si sovrappone con le performance pubbliche già presenti 

- non esiste già una performance per quell'artista

- l'ora di inizio è dopo le 14:00 (orario inizio festival) e ora inizio > ora fine

- la data ed il palco sono validi e genere e descrizioni non sono nulli

- le immagini devono essere nei formati concessi : png, jpg, jpeg, SVG, WebP, webp, avif.
</p>


Una performance con **visibilità privata (bozza)** viene creata se rispetta i vincoli precedenti ma viene **omesso il controllo sulle possibili sovrapposizioni**, sarà poi posticipato quando si vorrà passare da bozza a pubblica.

<br>Sarà possibile inoltre eliminare performance pubbliche, modificare / eliminare / pubblicare le proprie bozze direttamente dalla pagina profilo dell'organizzatore.

### Gestione dei biglietti
Per quanto riguarda l'acquisto del singolo biglietto non ci sono state scelte differenti rispetto alle specifiche.


## Credenziali utenti di test

Vengono fornite le credenziali di tre partecipanti (devastasi@gmail.com contiene una bozza) e quelle di tre partecipanti che hanno acquistato tre tipologie di biglietti diversi.

### Organizzatori 
* email: boniolo.adrian@gmail.com Password: Password1  (bozza Domenica 22)
* email jsaenz@gmail.com Password: Password2 (bozza Sabato 21)
* email devastasi@gmail.com Password: Password3 (bozza Venerdì 20)

### Partecipanti
* email: matteocastigliego@gmail.com Password: Password3

* email: caffa@gmail.com Password: Password5
* email: calvello@gmail.com Password: Password6

## Requirements 
* Flask frame per creare web app in Python
* Werkzeug	Flask per routing, 
* Jinja2	usato da Flask per generare HTML dinamico.
* MarkupSafe rende sicuri gli output HTML nei template.
* itsdangerous usato per gestire token (esempio password)
* Flask-Login gestisce autenticazione, login/logout e protezione delle route
* click per gestire il Flask CLI (interfaccia a linea di comando)
* colorama aggiunge colore all'output del terminale
* blinker segnali/eventi usato da Flask internamente 
* pillow usata per elaborare immagini, ridimensionarle e salvarle

## Indirizzo web app su Pythonanywhere
L'applicazione sarà visibile sino alla data '08-09-2025' al seguente indirizzo https://adrianboniolo.pythonanywhere.com/


## Struttura del progetto

`````text
festival-musicale-iaw/
├── static/
│   ├── images/                       # Immagini 
│   └── styles/                       # Risorse CSS
├── templates/
│   ├── base.html                     # Template base
│   ├── biglietti.html                # Home
│   ├── dettaglio_performance.html    # Dettaglio performance
│   ├── faq.html                      # Pagina Faq 
│   ├── login.html                    # Pagina Login
│   ├── about.html                    # Pagina about
│   ├── signup.html                   # Pagina registrazione
│   ├── profilo_partecipante.html     # Profilo partecipante
│   └── profilo_organizzatore.html    # Profilo organizzatore
│ 
│── acquisti_dao.py                   # Query acquisto ticket
│── performances_dao.py               # Query per performances
│── utenti_dao.py                     # Query sugli utenti
│── palchi_dao.py                     # Query sui palchi
│── immagini_dao.py                   # Query per immagini
│── biglietti_dao.py                  # Query biglietti
│── models.py                         # Modella gli oggetti usati
├── app.py                            # Entry point dell’app 
├── soundwave.db                      # Database SQLite locale
├── README.md                         # Documentazione progetto
`````

## Descrizione del progetto

L'applicazione web sviluppata ha l’obiettivo di gestire un **festival musicale annuale** che si svolge in un weekend (da venerdì a domenica). L'applicazione supporta due tipi di utenti registrati: **partecipanti** e **organizzatori**. Un utente non registrato può navigare liberamente il sito, ma non acquistare biglietti né gestire eventi.


## Diagramma Entità-Relazione
![diagramma_er](/static/images/er_db.png)
