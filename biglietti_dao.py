import sqlite3

def nuovo_biglietto(tipo, id_utente, start_date):

    sql = "INSERT INTO biglietti (tipo, id_utente, start_date) VALUES (?, ?, ?)"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql,(tipo, id_utente, start_date))

    conn.commit()

    cursor.close()
    conn.close()

# query che calcola numero biglietti per ven


# query che calcola numero biglietti per sab

def biglietti_dom():
    sql = """
        SELECT COUNT(*) 
        FROM biglietti 
        WHERE tipo = 'full_pass' 
            OR (tipo = 'due_giorni' AND start_date = 'Sabato 21 Giugno / Domenica 22 Giugno')
            OR (tipo = 'giornaliero' AND start_date = 'Domenica 22 Giugno')
    """
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count

# biglietti_dao.py

def count_biglietti(tipo, start_date=None):
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()

    if tipo == 'full_pass':
        sql = "SELECT COUNT(*) FROM biglietti WHERE tipo = 'full_pass'"
        cursor.execute(sql)
    elif tipo == 'due_giorni' and start_date:
        sql = "SELECT COUNT(*) FROM biglietti WHERE tipo = 'due_giorni' AND start_date = ?"
        cursor.execute(sql, (start_date,))
    elif tipo == 'giornaliero' and start_date:
        sql = "SELECT COUNT(*) FROM biglietti WHERE tipo = 'giornaliero' AND start_date = ?"
        cursor.execute(sql, (start_date,))
    else:
        return 0

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return count

def count_biglietti_per_giorno(giorno):
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()

    sql = """
    SELECT COUNT(*) FROM biglietti
    WHERE 
        (tipo = 'giornaliero' AND start_date = ?)
        OR 
        (tipo = 'due_giorni' AND start_date LIKE ?)
        OR 
        (tipo = 'full_pass' AND ? = 'Venerdì 20 Giugno')
    """

    # per "LIKE" serve includere il giorno nella stringa
    cursor.execute(sql, (giorno, f"%{giorno}%", giorno))
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return count


