import sqlite3
# inserisce un acquisto nel db
def nuovo_acquisto(id_utente, id_biglietto, data):

    sql = "INSERT INTO acquisti (id_utente, id_biglietto, data) VALUES (?, ?, ?)"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_utente, id_biglietto, data))

    conn.commit()

    cursor.close()
    conn.close()

# si occupa di verificare se un partecipante ha acquistato un biglietto o meno. In caso affermativo restituisce l'id del biglietto altrimenti None
def verifica_acquisto_utente(id_utente):

    sql = "SELECT id_biglietto FROM acquisti WHERE id_utente = ?"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_utente,))

    res = cursor.fetchone()

    cursor.close()
    conn.close()

    return res[0] if res else None # è una tupla
    
# dato l'id del partecipante  
def get_biglietto_utente(id_utente):
     
     sql = "SELECT id_biglietto, data FROM acquist WHERE id_utente = ? "

     conn = sqlite3.connect("soundwave.db")

     cursor = conn.cursor()
     cursor.execute(sql, (id_utente,))
    
     res = cursor.fetchone()

     conn.close()
     cursor.close()

     return res

# query che si occupa di inserire un biglietto per un partecipante nella tabella acquisti
def insert_acquisto(id_utente, id_biglietto, data):

    sql = "INSERT into acquisti (id_utente, id_biglietto, data) VALUES (?,?,?)"

    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_utente, id_biglietto, data))

    conn.commit()

    conn.close()
    cursor.close()

# date diverse festival
def get_date_festival():

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    
    sql = """
    SELECT DISTINCT single_day as data FROM biglietti WHERE single_day IS NOT NULL
    UNION
    SELECT DISTINCT double_first as data FROM biglietti WHERE double_first IS NOT NULL  
    UNION
    SELECT DISTINCT double_second as data FROM biglietti WHERE double_second IS NOT NULL
    ORDER BY data
    """
    
    conn = sqlite3.connect("soundwave.db")
    
    cursor = conn.cursor()

    cursor.execute(sql)

    results = cursor.fetchall()

    
    cursor.close()
    conn.close()

    return [row[0] for row in results if row[0]]

# conto i biglietti per ciascuna data
def count_biglietti_per_data():

    date_festival = get_date_festival()
    
    conteggio_per_data = {data: 0 for data in date_festival} # inizializzo a 0

    sql = """
    SELECT 
        b.tipo,
        b.single_day,
        b.double_first, 
        b.double_second,
        COUNT(a.id_utente) as num_biglietti
    FROM acquisti a
    JOIN biglietti b ON a.id_biglietto = b.id
    GROUP BY b.id
    """
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql)

    results = cursor.fetchall()

    cursor.close()
    conn.close()
    
    # itero
    for tipo, single_day, double_first, double_second, num_biglietti in results:
        # cerco data giusta e +1
        if tipo == "Giornaliero" and single_day:
            if single_day in conteggio_per_data:
                conteggio_per_data[single_day] += num_biglietti
        # + 1 nelle date

        elif tipo == "Due giorni" and double_first and double_second:
            if double_first in conteggio_per_data:
                conteggio_per_data[double_first] += num_biglietti
            if double_second in conteggio_per_data:
                conteggio_per_data[double_second] += num_biglietti
        # +1 in tutte le date
        elif tipo == "Full pass":
            for data in date_festival:
                conteggio_per_data[data] += num_biglietti
    
    return conteggio_per_data
        
def get_biglietto_utente(id_utente):

    sql = "SELECT id_biglietto, data FROM acquisti WHERE id_utente = ?"  

    conn = sqlite3.connect("soundwave.db")
    cursor = conn.cursor()
    cursor.execute(sql, (id_utente,))
    
    res = cursor.fetchone()

    cursor.close()
    conn.close()

    return res

def verifica_disponibilita_biglietto(tipo, single_day=None, double_first=None, double_second=None):

    MAX_BIGLIETTI_PER_GIORNO = 200
    
   
    # date da verificare in base al tipo di biglietto
    date_da_verificare = []
    
    if tipo == 'Giornaliero' and single_day:
        date_da_verificare = [single_day]
    elif tipo == 'Due giorni' and double_first and double_second:
        date_da_verificare = [double_first, double_second]
    elif tipo == 'Full pass':
        date_da_verificare = get_date_festival()
    else:
        return {
            'disponibile': False,
            'messaggio': 'Tipo di biglietto non valido',
            'dettagli': {}
        }
    
    dettagli_conteggio = {}
    date_non_disponibili = []
    
    for data in date_da_verificare:
        conteggio = count_biglietti_per_singola_data(data) # chiamo funzione
        dettagli_conteggio[data] = {
            'venduti': conteggio,
            'disponibili': MAX_BIGLIETTI_PER_GIORNO - conteggio,
            'disponibile': conteggio < MAX_BIGLIETTI_PER_GIORNO
        }
        
        if conteggio >= MAX_BIGLIETTI_PER_GIORNO:
            date_non_disponibili.append(data)
    
    if date_non_disponibili:
        return {
            'disponibile': False,
            'messaggio': f'Biglietti esauriti per le seguenti date: {", ".join(date_non_disponibili)}',
            'dettagli': dettagli_conteggio
        }
    else:
        return {
            'disponibile': True,
            'messaggio': 'Biglietto disponibile',
            'dettagli': dettagli_conteggio
        }
            
    

def get_statistiche_disponibilita():

    MAX_BIGLIETTI_PER_GIORNO = 200

    date_festival = get_date_festival()
    conteggi = count_biglietti_per_data()
    
    statistiche = {}
    
    for data in date_festival:
        venduti = conteggi.get(data, 0)
        disponibili = MAX_BIGLIETTI_PER_GIORNO - venduti
        percentuale_venduta = (venduti / MAX_BIGLIETTI_PER_GIORNO) * 100
        
        statistiche[data] = {
            'venduti': venduti,
            'disponibili': max(0, disponibili),  
            'totale': MAX_BIGLIETTI_PER_GIORNO,
            'percentuale_venduta': round(percentuale_venduta, 1),
            'disponibile': venduti < MAX_BIGLIETTI_PER_GIORNO
        }
    
    return statistiche

# conto il numero di biglietti per singola data
def count_biglietti_per_singola_data(data_specifica):

    sql = """
            SELECT 
                b.tipo,
                b.single_day,
                b.double_first, 
                b.double_second,
                COUNT(a.id_utente) as num_biglietti
            FROM acquisti a
            JOIN biglietti b ON a.id_biglietto = b.id
            WHERE (
                (b.tipo = 'Giornaliero' AND b.single_day = ?) OR
                (b.tipo = 'Due giorni' AND (b.double_first = ? OR b.double_second = ?)) OR
                (b.tipo = 'Full pass')
            )
            GROUP BY b.id
            """
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()
    

    cursor.execute(sql, (data_specifica, data_specifica, data_specifica))
        
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    conteggio = 0
        
    date_festival = get_date_festival()  
        
    for tipo, single_day, double_first, double_second, num_biglietti in results:
        if tipo == "Full pass" and data_specifica in date_festival:
            conteggio += num_biglietti
        else:
            conteggio += num_biglietti
    
    return conteggio

# per mostrarlo sul biglietto in area personale
def get_data_acquisto(id_utente):

    sql = """
            SELECT data
            FROM acquisti
            WHERE id_utente = ?
            """
    
    conn = sqlite3.connect("soundwave.db")

    cursor = conn.cursor()

    cursor.execute(sql, (id_utente,))

    res = cursor.fetchone()

    cursor.close()
    conn.close()

    str = res[0]
    data, orario = str.split(' ')

    return data, orario