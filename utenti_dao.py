import sqlite3

# query per creare il nuovo utente

def nuovo_utente(u_nome, u_cognome, u_email, u_password, u_tipo):

    sql = "INSERT INTO utenti (nome, cognome, email, password, tipo) VALUES (?, ?, ?, ?, ?)"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (u_nome, u_cognome, u_email, u_password, u_tipo))

    conn.commit()
    cursor.close()
    conn.close()


# restituisce utenti per email
def get_utente_email(u_email):

    sql ="SELECT * FROM utenti WHERE email = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (u_email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


# restituisce utenti per id 
def get_utente_id(u_id):

    sql ="SELECT * FROM utenti WHERE id = ?"

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (u_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user
