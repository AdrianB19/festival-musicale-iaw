import sqlite3

# aggiunge performance nel db
def nuova_performance(data, ora_inizio, ora_fine,  descrizione, nome_artista, img_artista, genere, is_visibile, id_palco, id_organizzatore):

    sql = """INSERT INTO performances (data, ora_inizio, ora_fine, descrizione, 
            nome_artista,img_artista, genere, is_visibile, 
            id_palco, id_organizzatore) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine,  descrizione, nome_artista,img_artista, genere, is_visibile, id_palco, id_organizzatore))

    conn.commit()

    new_id = cursor.lastrowid
    
    cursor.close()
    conn.close()

    return new_id

# performances pubbliche ordinate per giorno decrescente ed ora decrescente
def get_performances_pubbliche():
    sql = """
        SELECT
            p1.id,
            p1.data,
            p1.ora_inizio,
            p1.ora_fine,
            p1.descrizione,
            p1.nome_artista,
            p1.img_artista,
            p1.genere,
            p2.nome AS nome_palco,
            p1.id_organizzatore
        FROM performances p1
        JOIN palchi p2 ON p1.id_palco = p2.id
        WHERE p1.is_visibile = 1
        ORDER BY
            p1.data ASC,
            p1.ora_inizio ASC,
            p1.ora_fine ASC
    """

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

# vedo sovrapposizione
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

# performances ordinate da far vedere nell'area organizzatore relative all'org
def get_performances_pubbliche_organizzatore(id_organizzatore):
    sql = """
    SELECT
        p1.id,
        p1.data,
        p1.ora_inizio,
        p1.ora_fine,
        p1.descrizione,
        p1.nome_artista,
        p1.img_artista,
        p1.genere,
        p2.nome AS nome_palco,
        p1.id_organizzatore
    FROM performances p1
    JOIN palchi p2 ON p1.id_palco = p2.id
    WHERE p1.is_visibile = 1 AND id_organizzatore = ?
    ORDER BY
        p1.data ASC,
        p1.ora_inizio ASC,
        p1.ora_fine ASC
"""
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_organizzatore,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# bozze organizzatore
def get_bozze_organizzatore(id_organizzatore):
    sql ="""
    SELECT
        p1.id,
        p1.data,
        p1.ora_inizio,
        p1.ora_fine,
        p1.descrizione,
        p1.nome_artista,
        p1.img_artista,
        p1.genere,
        p2.nome AS nome_palco,
        p1.id_organizzatore
    FROM performances p1
    JOIN palchi p2 ON p1.id_palco = p2.id
    WHERE p1.is_visibile = 0 AND id_organizzatore = ?
    ORDER BY
        p1.data ASC,
        p1.ora_inizio ASC,
        p1.ora_fine ASC
"""

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (id_organizzatore,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# perf pubbliche data + palco
def get_performances_pubbliche_data_palco(data, id_palco):
    sql = "SELECT * FROM performances WHERE is_visibile = 1 AND data = ? AND id_palco = ?"
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (data, id_palco))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

# eliminare performance se serve
def elimina_performance(id_performance):
    sql = "DELETE FROM performances WHERE id = ?"
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    cursor.execute(sql, (id_performance,))
    conn.commit()

    cursor.close()
    conn.close()


def get_performance_by_id(id):

    conn = sqlite3.connect("soundwave.db")

    conn.row_factory = sqlite3.Row  

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM performances WHERE id = ?", (id,))

    bozza = cursor.fetchone()

    cursor.close()
    conn.close()

    return bozza

# aggiorna bozza
def aggiorna_bozza(id, data, ora_inizio, ora_fine, descrizione, 
                   nome_artista, img_artista_url, 
                   genere, visibilita, id_palco):
    
    sql = """
        UPDATE performances
        SET data = ?, ora_inizio = ?, ora_fine = ?, descrizione = ?, 
            nome_artista = ?, img_artista = ?, 
            genere = ?, is_visibile = ?, id_palco = ?
        WHERE id = ?
    """

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (data, ora_inizio, ora_fine, descrizione,
                         nome_artista, img_artista_url,
                         genere, visibilita, id_palco, id))
    conn.commit()
    cursor.close()
    conn.close()

# mette perf pubblica
def pubblica_performance(id):

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute("UPDATE performances SET is_visibile = 1 WHERE id = ?", (id,))

    conn.commit()

    cursor.close()
    conn.close()

# artista esiste
def artista_esiste(nome_artista):

    sql = "SELECT 1 FROM performances WHERE nome_artista = ?"
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (nome_artista,))
    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return exists
