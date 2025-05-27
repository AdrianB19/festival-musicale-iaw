import sqlite3

# aggiunge performance nel db
def nuova_performance(data, ora_inizio, ora_fine, genere, descrizione, visibilita, id_palco, id_utente):
    """
    Inserisce una nuova performance nel database.
    """
    sql = """
        INSERT INTO performances 
        (data, ora_inizio, ora_fine, genere, descrizione, visibilita, id_palco, id_utente) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine, genere, descrizione, visibilita, id_palco, id_utente))
    conn.commit()
    
    cursor.close()
    conn.close()

# restituisce le performance 
def get_performance_pubbliche():

    sql = """
        SELECT * FROM performances 
        WHERE visibilita = 1 
        ORDER BY data, ora_inizio
    """
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)

    performances = cursor.fetchall()

    cursor.close()
    conn.close()

    return performances


# restituisce tutte le performance per un dato organizzatore
def get_performance_organizzatore(id_utente):

    sql = "SELECT * FROM performances WHERE id_utente = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_utente,))

    performances = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return performances
