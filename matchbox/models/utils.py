import re
import uuid
import iso8601
from firebase_admin import firestore


class GeoPointValue:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def parse(self):
        return firestore.GeoPoint(self.latitude, self.longitude)


def convert_name(name):
    return re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()


def generate_id():
    return uuid.uuid4().hex


def google_datetime_to_datetime(gfd):
    return iso8601.parse_date(gfd.isoformat())
