# 🎶 festival-musicale-iaw

Progetto d’esame per il corso **Introduzione alle Applicazioni Web** presso il Politecnico di Torino (Giugno 2025).

---

## 📖 Descrizione del progetto

L'applicazione web sviluppata ha l’obiettivo di gestire un **festival musicale annuale** che si svolge in un weekend (da venerdì a domenica). L'applicazione supporta due tipi di utenti registrati: **partecipanti** e **organizzatori**. Un utente non registrato può navigare liberamente il sito, ma non acquistare biglietti né gestire eventi.

---

## 🗃️ Utilizzo del database

L’applicazione utilizza un database relazionale (es. SQLite) per archiviare in modo persistente i dati relativi a:

- Utenti (partecipanti e organizzatori)
- Performance musicali
- Biglietti acquistati
- Palchi disponibili
- Immagini disponibili per la performance

### 📝 Diagramma Entità-Relazione
![diagramma_er](/static/images/er_db.png)

### 👥 Tipi di utenti

- **Partecipanti**
  - Possono registrarsi/login (identificati univocamente tramite email)
  - Possono acquistare **un solo tipo di biglietto per edizione**
  - Visualizzano i biglietti acquistati nel proprio profilo
  - Non possono modificare performance

- **Organizzatori**
  - Possono creare e modificare le proprie performance (solo se non pubblicate)
  - Possono pubblicare performance che diventano visibili a tutti
  - Accedono alle statistiche di vendita dei biglietti
  - Non possono acquistare biglietti

- **Visitatori non registrati**
  - Possono visualizzare le performance pubblicate
  - Non possono acquistare biglietti né creare eventi

---

### 🎤 Gestione delle performance

Ogni performance musicale contiene i seguenti campi:

- Nome dell’artista o gruppo (univoco nel festival)
- Giorno e ora di inizio (venerdì, sabato o domenica)
- Durata prevista (in minuti)
- Descrizione
- Nome del palco (tra quelli disponibili)
- Genere musicale
- Una o più immagini promozionali
- Stato: **bozza** o **pubblicata**

#### 🔒 Vincoli applicati

- Un artista può esibirsi **una sola volta per edizione**
- Non possono esserci **sovrapposizioni temporali** sullo stesso palco
- Una performance **pubblicata non è più modificabile ma eliminabile dall'organizzatore**
- Gli organizzatori possono modificare **solo le proprie performance** in bozza

---

### 🎟️ Tipi di biglietti

- **Biglietto Giornaliero** (valido per un giorno a scelta)
- **Pass 2 Giorni** (valido per due giorni consecutivi)
- **Full Pass** (valido per tutti e tre i giorni)

#### 🔒 Vincoli sui biglietti

- Un partecipante può acquistare **un solo biglietto per edizione**
- I biglietti **non sono modificabili né rimborsabili**
- Ogni giorno ha un **massimo di 200 partecipanti** ammessi

---

### 🏠 Homepage e funzionalità utente

- La homepage mostra le performance **pubblicate**, ordinate per giorno e orario
- Sono disponibili **filtri** per giorno, palco e genere musicale
- Ogni performance è cliccabile per visualizzarne i dettagli
- La pagina profilo mostra:
  - Per i partecipanti: il biglietto acquistato e i giorni inclusi
  - Per gli organizzatori: performance create, pubblicate e bozze proprie

---

## 📁 Struttura del progetto

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
