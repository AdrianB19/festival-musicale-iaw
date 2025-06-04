# definisco le entità del db

from flask_login import UserMixin


# utente generico e con UserMixin permette di vedere se è autenticato
class User(UserMixin):
    def __init__(self, id, nome, cognome, email, password, tipo):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password = password
        self.tipo = tipo

# classe biglietto
class Biglietto:
    def __init__(self, id, tipo, single_day, double_first, double_second, prezzo):
        self.id = id
        self.tipo = tipo
        self.single_day = single_day
        self.double_first = double_first
        self.double_second = double_second
        self.prezzo = prezzo

# rappresenta la performance
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

class Palco:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome

class Acquisto:
    def __init__(self, id_utente, id_biglietto, data):
        self.id_utente = id_utente
        self.id_biglietto = id_biglietto
        self.id_utente = data
        