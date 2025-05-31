import sqlite3

# aggiunge performance nel db
def nuova_performance(data, ora_inizio, ora_fine,  descrizione, nome_artista, numero_artisti, img_artista, genere, is_visibile, id_palco, id_organizzatore):

    sql = """INSERT INTO performances (data, ora_inizio, ora_fine, descrizione, 
            nome_artista, numero_artisti, img_artista, genere, is_visibile, 
            id_palco, id_organizzatore) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine,  descrizione, nome_artista, numero_artisti, img_artista, genere, is_visibile, id_palco, id_organizzatore))

    conn.commit()

    new_id = cursor.lastrowid
    
    cursor.close()
    conn.close()

    return new_id


def get_performances_pubbliche():
    sql = """
        SELECT * FROM performances
        WHERE is_visibile = 1
        ORDER BY
            CASE data
                WHEN 'Venerdì 20 Giugno' THEN 1
                WHEN 'Sabato 21 Giugno' THEN 2
                WHEN 'Domenica 22 Giugno' THEN 3
                ELSE 4
            END DESC,
            ora_inizio DESC,
            ora_fine DESC
    """

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results



def get_performances_pubbliche_organizzatore(id_organizzatore):
    sql = """
        SELECT * FROM performances
        WHERE is_visibile = 1 AND id_organizzatore = ?
        ORDER BY
            CASE data
                WHEN 'Venerdì 20 Giugno' THEN 1
                WHEN 'Sabato 21 Giugno' THEN 2
                WHEN 'Domenica 22 Giugno' THEN 3
                ELSE 4
            END DESC,
            ora_inizio DESC
    """
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_organizzatore,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# 4. Tutte le bozze (non visibili) di un organizzatore
def get_bozze_organizzatore(id_organizzatore):
    sql = "SELECT * FROM performances WHERE is_visibile = 0 AND id_organizzatore = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (id_organizzatore,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# 5. Tutte le performances pubbliche in base a data e palco
def get_performances_pubbliche_data_palco(data, id_palco):
    sql = "SELECT * FROM performances WHERE is_visibile = 1 AND data = ? AND id_palco = ?"
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (data, id_palco))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def verifica_sovrapposizione(data, ora_inizio, ora_fine, id_palco):

    sql = """
        SELECT * FROM performances
        WHERE data = ?
        AND id_palco = ?
        AND is_visibile = 1
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
        WHERE is_visibile = 1
        ORDER BY data, id_palco, ora_inizio
    """
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results



def get_performance_by_id(id):

    conn = sqlite3.connect("soundwave.db")

    conn.row_factory = sqlite3.Row  

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM performances WHERE id = ?", (id,))

    bozza = cursor.fetchone()

    cursor.close()
    conn.close()

    return bozza


def aggiorna_bozza(id, data, ora_inizio, ora_fine, descrizione, 
                   nome_artista, numero_artisti, img_artista_url, 
                   genere, visibilita, id_palco):
    
    sql = """
        UPDATE performances
        SET data = ?, ora_inizio = ?, ora_fine = ?, descrizione = ?, 
            nome_artista = ?, numero_artisti = ?, img_artista = ?, 
            genere = ?, is_visibile = ?, id_palco = ?
        WHERE id = ?
    """

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine, descrizione,
                         nome_artista, numero_artisti, img_artista_url,
                         genere, visibilita, id_palco, id))
    conn.commit()
    cursor.close()
    conn.close()



def pubblica_performance(id):

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute("UPDATE performances SET is_visibile = 1 WHERE id = ?", (id,))

    conn.commit()

    cursor.close()
    conn.close()

def artista_esiste(nome_artista):

    sql = "SELECT 1 FROM performances WHERE nome_artista = ?"
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (nome_artista,))
    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return exists
