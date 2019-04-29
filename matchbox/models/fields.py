import datetime
import google
from matchbox.database import db
from matchbox.models import utils as models_utils
from matchbox.models import field_validator
from matchbox.models import error


class Field:

    allowed_attributes = []

    def __init__(self, *args, **kwargs):
        self.field_validator = field_validator.FieldValidator(
            self, kwargs or {}
        )

    def add_to_class(self, klass, name):
        self.name = name
        setattr(klass, name, None)

    def lookup_value(self, lookup_type, value):
        val = self.field_validator.validate(self.name, value)
        if val is None:
            return val
        return self.db_value(val)

    def db_value(self, value):
        raise NotImplementedError()

    def python_value(self, value):
        raise NotImplementedError()


class IDField(Field):

    @staticmethod
    def random_id():
        return models_utils.generate_id()

    def db_value(self, value):
        try:
            return str(value)
        except ValueError:
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    str,
                    type(value)
                ))

    def python_value(self, value):
        return str(value) or None


class IntegerField(Field):
    allowed_attributes = ['blank', 'default']

    def db_value(self, value):
        try:
            return int(value)
        except ValueError:
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    int,
                    type(value)
                ))

    def python_value(self, value):
        if value is not None:
            return int(value)


class TextField(Field):
    allowed_attributes = ['blank', 'default', 'max_length']

    def db_value(self, value):
        try:
            return str(value)
        except ValueError:
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    str,
                    type(value)
                ))

    def python_value(self, value):
        return value


class TimeStampField(Field):
    allowed_attributes = ['blank', 'default']

    def db_value(self, value):
        if not isinstance(value, datetime.datetime):
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    datetime.datetime,
                    type(value)
                ))
        return value

    def python_value(self, value):
        return models_utils.google_datetime_to_datetime(value)


class BooleanField(Field):
    allowed_attributes = ['blank', 'default']

    def db_value(self, value):
        return True if value else False

    def python_value(self, value):
        return value


class ListField(Field):
    allowed_attributes = ['blank', 'default']

    def db_value(self, value):
        if not isinstance(value, list):
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    list,
                    type(value)
                ))
        return value

    def python_value(self, value):
        return value


class MapField(Field):
    allowed_attributes = ['blank', 'default']

    def db_value(self, value):
        if not isinstance(value, dict):
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    dict,
                    type(value)
                ))
        return value

    def python_value(self, value):
        return value


class GeoPointField(Field):
    allowed_attributes = ['blank', 'default']

    def db_value(self, value):
        if not isinstance(value, models_utils.GeoPointValue):
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    models_utils.GeoPointValue,
                    type(value)
                ))
        return value.parse()

    def python_value(self, value):
        if value is None:
            return None

        return models_utils.GeoPointValue(
            latitude=value.latitude, longitude=value.longitude
        )


class ReferenceField(Field):
    def __init__(self, ref_model):
        super().__init__()
        self.ref_model = ref_model

    def lookup_value(self, lookup_type, value):
        if value is None:
            return None
        return self.db_value(value)

    def db_value(self, value):
        if not issubclass(value.__class__, self.ref_model):
            raise error.DBTypeError(
                '{} required value type {}, get {}'.format(
                    self.__class__.__name__,
                    self.ref_model.__class__.__name__,
                    type(value)
                )
            )
        return google.cloud.firestore_v1.document.DocumentReference(
                    self.name, value.id, client=db.conn
                )

    def python_value(self, value):
        return value
