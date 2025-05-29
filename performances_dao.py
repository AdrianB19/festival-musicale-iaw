import sqlite3

# aggiunge performance nel db
def nuova_performance(data, ora_inizio, ora_fine, genere, descrizione, is_visible, id_palco, id_organizzatore):

    sql = """INSERT INTO performances (data, ora_inizio, ora_fine, descrizione, 
            nome_artista, numero_artisti, img_artista, genere, is_visibile, 
            id_palco, id_organizzatore) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine, genere, descrizione, is_visible, id_palco, id_organizzatore))

    conn.commit()

    cursor.close()
    conn.close()


# 2. Tutte le performances pubbliche
def get_performances_pubbliche():
    sql = "SELECT * FROM performances WHERE is_visible = 1"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# 3. Tutte le performances pubbliche di un organizzatore
def get_performances_pubbliche_organizzatore(id_organizzatore):
    sql = "SELECT * FROM performances WHERE is_visible = 1 AND id_organizzatore = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_organizzatore,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# 4. Tutte le bozze (non visibili) di un organizzatore
def get_bozze_organizzatore(id_organizzatore):
    sql = "SELECT * FROM performances WHERE is_visible = 0 AND id_organizzatore = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (id_organizzatore,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# 5. Tutte le performances pubbliche in base a data e palco
def get_performances_pubbliche_data_palco(data, id_palco):
    sql = "SELECT * FROM performances WHERE is_visible = 1 AND data = ? AND id_palco = ?"
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (data, id_palco))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# 6. Verifica sovrapposizione tra performances (stessa data e palco con orari sovrapposti)
def verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco):

    sql = """
        SELECT * FROM performances
        WHERE data = ?
        AND id_palco = ?
        AND (
            (? < ora_fine AND ? > ora_inizio)
        )
    """
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (data, id_palco, ora_inizio, ora_fine))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# 7. Elimina una performance dato l'id
def elimina_performance(id_performance):
    sql = "DELETE FROM performances WHERE id = ?"
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (id_performance,))
    conn.commit()
    
    cursor.close()
    conn.close()

# 8. Ottiene tutte le performance pubbliche ordinate per data, palco e ora_inizio (ordine crescente)
def get_performances_pubbliche_ordinate():

    sql = """
        SELECT * FROM performances
        WHERE is_visible = 1
        ORDER BY data, id_palco, ora_inizio
    """
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

