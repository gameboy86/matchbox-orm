import firebase_admin
from firebase_admin import firestore

from matchbox.database import error


class Database:
    def __init__(self):
        self._conn = None

    def initialization(self, cert_path):
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = firebase_admin.credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)

        self._conn = firestore.client()

    @property
    def conn(self):
        if self._conn is None:
            raise error.DBDoesNotinitialized(
                'Connection to db must be initialized'
            )
        return self._conn


db = Database()


def db_initialization(cert_path):
    global db

    db.initialization(cert_path)
