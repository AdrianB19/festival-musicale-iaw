# definisco le entità del db

class User(UserMixin):
    def __init__(self, id, nome, cognome, email, password,tipo):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password = password
        self.tipo = tipo

class Biglietto:
    def __init__(self, id, id_utente, tipo, giorni):
        self.id = id
        self.id_utente = id_utente
        self.tipo = tipo  # "giornaliero", "2giorni", "full"
        self.giorni = giorni  # es. "ven", "sab,dom"

class Performance:
    def __init__(self, id, id_artista, giorno, orario, durata, descrizione, palco, genere, pubblicata, id_organizzatore):
        self.id = id
        self.id_artista = id_artista
        self.giorno = giorno  # "ven", "sab", "dom"
        self.orario = orario  # "14:00", "18:30"
        self.durata = durata  # in minuti
        self.descrizione = descrizione
        self.palco = palco  # es. "Palco A"
        self.genere = genere  # es. "Rock", "Pop", "Jazz"
        self.pubblicata = pubblicata  # booleano (0 = bozza, 1 = pubblicata)
        self.id_organizzatore = id_organizzatore

class Artista:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome

class Palco:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome

class Immagine:
    def __init__(self, id, id_performance, path):
        self.id = id
        self.id_performance = id_performance
        self.path = path  # percorso immagine, es. "/static/images/img1.jpg"
