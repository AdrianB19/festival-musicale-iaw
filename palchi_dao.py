import sqlite3

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




