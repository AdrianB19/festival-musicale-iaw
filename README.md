# festival-musicale-iaw
Progetto dell'esame relativo al corso Introduzione alle Applicazioni Web per il Politecnico di Torino (Giugno 2025).

# Descrizione del progetto

## 📁 Descrizione dei file e delle cartelle

- `static/`  
  Contiene tutti i file statici visibili dal client:
  - `images/`: immagini usate nel sito (loghi, banner, icone)
  - `templates/`: CSS, JS o risorse statiche aggiuntive

- `templates/`  
  Template HTML renderizzati da Flask, uno per ogni pagina del sito:
  - `index.html`: homepage del festival
  - `eventi.html`: elenco eventi, artisti, location
  - `contatti.html`: modulo contatto/info

- `app.py`  
  File principale della web app. Contiene la logica Flask (routing, server, connessione DB)

- `soundwave.db`  
  Database locale per archivio dei dati, con DB Browser for SQL Lite

- `dao/`  
  DAO = Data Access Object. Qui si gestisce l'accesso e la manipolazione dei dati:
  - `eventi_dao.py`: funzioni per leggere/scrivere eventi
  - `utenti_dao.py`: funzioni per la gestione degli utenti

- `README.md`  
  Documentazione del progetto, istruzioni di avvio e info generali.




## 📝​Scelta della base di dati
![diagramma_er](/static/images/er_festival.png)
Gli utenti sono divisi in due categorie, partecipanti ed organizzatori. Un partecipante può comperare un solo biglietto, per dei quali si tiene traccia del tipo (full pass, due giorni, giornaliero).
Gli organizzatori possono creare più performances delle quali son noti giorno, ora di inizio e di fine, una descrizione, una o più foto, la visibilità ed anche il genere.
Si tiene traccia anche dell'artista (o gruppo di artisti) che partecipa alla performance ed il palco presso quest'ultima prende luogo. 

## Scelte implementative

# Utilizzo


