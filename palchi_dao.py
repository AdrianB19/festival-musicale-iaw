import sqlite3

# inserisco un nuovo palco
def nuovo_palco(nome):

    sql = "INSERT INTO palchi (nome) VALUES (?)"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (nome,))

    conn.commit()
    
    cursor.close()
    conn.close()

# ritorno tutti i palchi nel DB 
def get_palchi():

    sql = "SELECT * FROM palchi ORDER BY id ASC"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql)

    palchi = cursor.fetchall()

    cursor.close()
    conn.close()

    return palchi




