# festival-musicale-iaw

Progetto d’esame per il corso **Introduzione alle Applicazioni Web** presso il Politecnico di Torino (Giugno 2025).

---

## Descrizione del progetto

L'applicazione web sviluppata ha l’obiettivo di gestire un **festival musicale annuale** che si svolge in un weekend (da venerdì a domenica). L'applicazione supporta due tipi di utenti registrati: **partecipanti** e **organizzatori**. Un utente non registrato può navigare liberamente il sito, ma non acquistare biglietti né gestire eventi.


### Diagramma Entità-Relazione
![diagramma_er](/static/images/er_db.png)

## Istruzioni sulla navigazione
Per quanto

### Gestione delle performance

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
## Credenziali utenti di test

### Organizzatori 
* email: boniolo.adrian@gmail.com Password: Password1
* email jsaenz@gmail.com Password: Password2
* email devastasi@gmail.com Password: Password3

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

