import re
import uuid
import iso8601
import google

from firebase_admin import firestore

from matchbox import database


class GeoPointValue:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def parse(self):
        return firestore.GeoPoint(self.latitude, self.longitude)


def convert_name(name):
    return re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()


def google_datetime_to_datetime(gfd):
    return iso8601.parse_date(gfd.isoformat())


def get_reference_fields(collection, value, db=None):
    if db is None:
        db = database.db

    return google.cloud.firestore_v1.document.DocumentReference(
        collection,
        value,
        client=db.conn
    )
