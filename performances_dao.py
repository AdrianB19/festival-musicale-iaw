import sqlite3
import os
from datetime import datetime

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

# performances pubbliche ordinate per giorno decrescente ed ora decrescente e ritorno nome del palco per usarlo con jinja
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

# ritorno i dettagli di una performance usate nel dettaglio, dato il suo id
def get_performance_by_id(id):

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
            p2.nome AS nome_palco
        FROM performances p1
        JOIN palchi p2 ON p1.id_palco = p2.id
        WHERE p1.is_visibile = 1 AND p1.id = ?
    """

    conn = sqlite3.connect("soundwave.db")

    conn.row_factory = sqlite3.Row  

    cursor = conn.cursor()

    cursor.execute(sql, (id,))

    perf = cursor.fetchone()

    cursor.close()
    conn.close()

    return perf

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

# ritorno i dettagli di una bozza
def get_bozza_by_id(id):

    sql = "SELECT * FROM performances WHERE id = ? AND is_visibile = 0"

    conn = sqlite3.connect("soundwave.db")

    conn.row_factory = sqlite3.Row  

    cursor = conn.cursor()

    cursor.execute(sql, (id,))

    bozza = cursor.fetchone()

    cursor.close()
    conn.close()

    return bozza

# mette perf pubblica
def pubblica_performance(id):

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute("UPDATE performances SET is_visibile = 1 WHERE id = ?", (id,))

    conn.commit()

    cursor.close()
    conn.close()

# artista esiste nel db
def artista_esiste(nome_artista):

    sql = "SELECT 1 FROM performances WHERE nome_artista = ?"
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (nome_artista,))
    
    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return exists

# dà l'id della performance
def get_id_by_artista(nome_artista):

    sql = "SELECT id FROM performances WHERE nome_artista = ? "

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (nome_artista,))

    res = cursor.fetchone()

    cursor.close()
    conn.close()

    return res[0] if res else None

# prendo tutti i generi diversi
def get_generi_disponibili():

    sql = """
          SELECT DISTINCT genere
          FROM performances
          WHERE is_visibile = 1 AND genere is NOT NULL
          ORDER BY genere ASC
          """
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql)

    res = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in res]

# ottieni tutte le date distinte delle performances pubbliche
def get_date_disponibili():

    sql = """
        SELECT DISTINCT data
        FROM performances
        WHERE is_visibile = 1
        ORDER BY data ASC
    """
    
    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # formatta le date usando la stessa logica di biglietti_dao.py
    date_formattate = []
    for row in results:
        data_iso = row[0]
        
        # Parsing della data
        data = datetime.strptime(data_iso, "%Y-%m-%d")
        
        giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
        mesi = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
        
        giorno_settimana = giorni[data.weekday()]
        mese = mesi[data.month - 1]
        giorno_numero = data.day
        
        giorno_formattato = f"{giorno_settimana} {giorno_numero} {mese}"
        
        date_formattate.append({
            'iso': data_iso,
            'formattata': giorno_formattato
        })
    
    return date_formattate

# performances pubbliche con filtri
def get_performances_filtrate(palco_id=None, data=None, genere=None):
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
    """
    
    params = []
    
    # se ho messo palco nel filtro, data e genere e non sono nulli li aggiungo alla query
    if palco_id:
        sql += " AND p1.id_palco = ?"
        params.append(palco_id)
    
    if data:
        sql += " AND p1.data = ?"
        params.append(data)
    
    if genere:
        sql += " AND p1.genere = ?"
        params.append(genere)
    
    sql += """
        ORDER BY
            p1.data ASC,
            p1.ora_inizio ASC,
            p1.ora_fine ASC
    """
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, params)
    
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return results

# eliminare performance se serve
def elimina_performance(id_performance):

    sql = "SELECT img_artista FROM performances WHERE id = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_performance,))
    result = cursor.fetchone()

    if result and result[0]:
        img_path_db = result[0]
        img_filename = os.path.basename(img_path_db)
        full_path = os.path.join("static", "images", img_filename)
        os.remove(full_path)

    sql = "DELETE FROM performances WHERE id = ?"
    
    cursor.execute(sql, (id_performance,))

    conn.commit()

    cursor.close()
    conn.close()