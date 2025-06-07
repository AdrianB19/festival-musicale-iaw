import sqlite3

def get_immagini_performance(id_perf):
    
    sql = "SELECT url_immagine FROM has_immagini WHERE id_performance = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_perf,))

    res = cursor.fetchall()

    cursor.close()
    conn.close()

    return res if res else None

def insert_immagine(id_performance, url_immagine):

    sql = "INSERT INTO has_immagini (id_performance, url_immagine) VALUES (?,?)"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_performance, url_immagine))

    conn.commit()

    cursor.close()
    conn.close()

def get_immagini_by_id_perf(id):

    sql = "SELECT url_immagine FROM has_immagini WHERE id_performance = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id,))

    res = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in res]

def update_immagine_perf(id, vecchio_url, nuovo_url ):

    sql = "UPDATE has_immagini SET url_immagine = ? WHERE id_performance = ? AND url_immagine = ?"
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (nuovo_url, id, vecchio_url))

    conn.commit()

    cursor.close()
    conn.close()

def get_immagini_perf(id_performance):
    sql = "SELECT url_immagine FROM has_immagini WHERE id_performance = ?"
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_performance,))
    res = cursor.fetchall() 
    cursor.close()
    conn.close()

    return [row[0] for row in res]
