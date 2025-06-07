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


        