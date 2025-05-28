import sqlite3

# query che aggiunge un biglietto nel db
def nuovo_biglietto(id_utente, tipo, giorni):

    sql = "INSERT INTO biglietti (id_utente, tipo, giorni) VALUES (?, ?, ?)"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_utente, tipo, giorni))
    
    conn.commit()
    cursor.close()
    conn.close()



# query che conta il numero di biglietti per giorno
def count_biglietti_giornalieri(giorno):

    sql = "SELECT COUNT(*) FROM biglietti WHERE giorni LIKE ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (f"%{giorno}%",))
    count = cursor.fetchone()[0] # estrae prima colonna prima riga 

    cursor.close()
    conn.close()

    return count

def get_biglietto_by_partecipante(id_partecipante):

    sql = "SELECT * FROM biglietti WHERE id_utente = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_partecipante,))

    biglietto = cursor.fetchone()

    cursor.close()
    conn.close()

    return biglietto
