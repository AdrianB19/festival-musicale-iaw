import sqlite3

# aggiungo una nuova immagine
def aggiungi_immagine_performance(id_performance, id_img):

    sql = "INSERT INTO has_immagini (id_performance, id_img) VALUES (?, ?)"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_performance, id_img))

    conn.commit()

    cursor.close()
    conn.close()


def get_immagini_di_performance(id_performance):

    sql = "SELECT id_img FROM has_immagini WHERE id_performance = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_performance,))

    immagini = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return immagini
