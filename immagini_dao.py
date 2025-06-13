import sqlite3
import os


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

def delete_immagini_performance(id_performance):
    
    select_sql = "SELECT url_immagine FROM has_immagini WHERE id_performance = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(select_sql, (id_performance,))

    immagini = cursor.fetchall()

    for img in immagini:
        nome_file_db = img[0]
        nome_file_locale = os.path.basename(nome_file_db)  # solo il nome del file
        path = os.path.join("static", "images", nome_file_locale)

        if os.path.exists(path):
            os.remove(path)
            print(f"Eliminato: {path}")
        else:
            print(f"File non trovato: {path}")

 

    sql = "DELETE FROM has_immagini WHERE id_performance = ?"
    cursor.execute(sql, (id_performance,))

    conn.commit()

    cursor.close()
    conn.close()
