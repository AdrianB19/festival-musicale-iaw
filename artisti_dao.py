import sqlite3

# inserisce un artista nel db
def nuovo_artista(nome, num_membri, img_artista):

    sql = "INSERT INTO artisti (nome, num_membri, img_artista) VALUES (?, ?, ?)"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (nome, num_membri, img_artista))

    conn.commit()

    cursor.close()
    conn.close()

# ritorna un artista per nome
def get_artista_by_nome(nome):

    sql = "SELECT * FROM artisti WHERE nome = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (nome,))

    artista = cursor.fetchone()

    cursor.close()
    conn.close()

    return artista

# get artista by id
def get_artista_by_id(id_artista):

    sql = "SELECT * FROM artisti WHERE id = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_artista,))

    artista = cursor.fetchone()

    cursor.close()
    conn.close()

    return artista

# ritorna tutti gli artisti
def get_tutti_gli_artisti():

    sql = "SELECT * FROM artisti ORDER BY nome"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql)

    artisti = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return artisti

