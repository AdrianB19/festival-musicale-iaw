import sqlite3

# aggiunge performance nel db
def nuova_performance(data, ora_inizio, ora_fine, genere, descrizione, visibilita, id_palco, id_utente):
    sql = "INSERT INTO performances (data, ora_inizio, ora_fine, genere, descrizione, visibilita, id_palco, id_utente) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine, genere, descrizione, visibilita, id_palco, id_utente))
    conn.commit()
    cursor.close()
    conn.close()

# restituisce tutte le performance pubblicate
def get_performance_pubbliche():
    sql = "SELECT * FROM performances WHERE visibilita = 1 ORDER BY data, ora_inizio"
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    performances = cursor.fetchall()
    cursor.close()
    conn.close()
    return performances

# restituisce tutte le performance dell'organizzatore
def get_performance_organizzatore(id_utente):
    sql = "SELECT * FROM performances WHERE id_utente = ? ORDER BY data, ora_inizio"
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_utente,))
    performances = cursor.fetchall()
    cursor.close()
    conn.close()
    return performances

# restituisce solo le bozze
def get_bozze_by_organizzatore(id_utente):
    sql = "SELECT * FROM performances WHERE id_utente = ? AND visibilita = 0 ORDER BY data, ora_inizio"
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_utente,))
    bozze = cursor.fetchall()
    cursor.close()
    conn.close()
    return bozze

# restituisce solo le performance pubblicate di un organizzatore
def get_performance_pubblicate_by_organizzatore(id_utente):
    sql = "SELECT * FROM performances WHERE id_utente = ? AND visibilita = 1 ORDER BY data, ora_inizio"
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_utente,))
    pubblicate = cursor.fetchall()
    cursor.close()
    conn.close()
    return pubblicate

# verifica se esiste una performance che si sovrappone
def verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco):
    sql = "SELECT COUNT(*) FROM performances WHERE data = ? AND id_palco = ? AND visibilita = 1 AND ((? BETWEEN ora_inizio AND ora_fine) OR (? BETWEEN ora_inizio AND ora_fine) OR (ora_inizio BETWEEN ? AND ?) OR (ora_fine BETWEEN ? AND ?))"
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, id_palco, ora_inizio, ora_fine, ora_inizio, ora_fine, ora_inizio, ora_fine))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result > 0
