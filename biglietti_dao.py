import sqlite3
from datetime import datetime

def formatta_data(data_str):
    
    data = datetime.strptime(data_str, "%Y-%m-%d")
    
    giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']

    mesi = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
            'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']

    giorno_settimana = giorni[data.weekday()]
    mese = mesi[data.month - 1]
    giorno_numero = data.day
    
    giorno_formattato = f"{giorno_settimana} {giorno_numero} {mese}"
    
    return data_str, giorno_formattato

def get_opzioni_biglietti():
 
    sql = "SELECT tipo, single_day, double_first, double_second, prezzo FROM biglietti"

    conn = sqlite3.connect("soundwave.db")
    
    cursor = conn.cursor()

    cursor.execute(sql)

    results = cursor.fetchall()

    cursor.close()
    conn.close()
    
    # Inizializzazione del dizionario finale da restituire al template
    # Ogni chiave corrisponde a un tipo di biglietto con una lista vuota
    opzioni = {
        "giornaliero": [],
        "due_giorni": [],
        "full_pass": [] 
    }
    
    # Iterazione attraverso tutti i record recuperati dal database
    # Ogni riga contiene: tipo, single_day, double_first, double_second, prezzo
    for tipo, single_day, double_first, double_second, prezzo in results:
        
        if tipo == "Giornaliero" and single_day:

            giorno_iso, giorno_testo = formatta_data(single_day)

            if giorno_iso and giorno_testo:

                opzioni["giornaliero"].append({
                    "tipo": tipo,
                    "giorno_iso": giorno_iso,
                    "giorno_testo": giorno_testo,
                    "prezzo": prezzo
                })

        elif tipo == "Due giorni" and double_first and double_second:

            giorno1_iso, giorno1_testo = formatta_data(double_first)
            giorno2_iso, giorno2_testo = formatta_data(double_second)
            
            if giorno1_iso and giorno1_testo and giorno2_iso and giorno2_testo:
                opzioni["due_giorni"].append({
                    "tipo": tipo,
                    "giorni_iso": [giorno1_iso, giorno2_iso],
                    "giorni_testo": f"{giorno1_testo} e {giorno2_testo}",
                    "prezzo": prezzo
                })

        elif tipo == "Full pass":

            opzioni["full_pass"].append({
                "tipo": tipo,
                "value": "full_pass",
                "label": "Pass completo festival",
                "prezzo": prezzo
            })

    return opzioni

# prende i dati di un biglietto
def get_biglietto(id_biglietto):

    sql = "SELECT tipo, single_day, double_first, double_second, prezzo FROM biglietti where id = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_biglietto,))

    biglietto = cursor.fetchone()

    cursor.close()
    conn.close()

    return biglietto

# uso questo modo per gestire il tipo dei biglietti (non è molto estendibile)
def get_id_biglietto(tipo, single_day, double_first, double_second):

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
      
    if tipo == 'Giornaliero':
        sql = """SELECT id FROM biglietti 
                    WHERE tipo = ? AND single_day = ? 
                    AND double_first IS NULL AND double_second IS NULL"""
        
        cursor.execute(sql, (tipo, single_day))
        
    elif tipo == 'Due giorni':
        sql = """SELECT id FROM biglietti 
                    WHERE tipo = 'Due giorni' AND double_first = ? AND double_second = ? 

                    AND single_day IS NULL"""
        cursor.execute(sql, (double_first, double_second))
        
    elif tipo == 'Full pass':
        sql = """SELECT id FROM biglietti 
                    WHERE tipo = 'Full pass'
                    AND single_day IS NULL 
                    AND double_first IS NULL 
                    AND double_second IS NULL"""
        
        cursor.execute(sql)
        
    else:
        return None
    
    risultato = cursor.fetchone()

    cursor.close()
    conn.close()

    return risultato