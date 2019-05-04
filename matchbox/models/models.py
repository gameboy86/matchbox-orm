from matchbox.models import utils

from matchbox.models import fields
from matchbox.queries import queries
from matchbox.models import managers


class BaseModel(type):
    def __new__(mcs, name, base, attrs):
        cls = super().__new__(mcs, name, base, attrs)

        class Meta:
            fields = {}
            managers_map = {}

            def __init__(self, model_class):
                self.model_class = model_class

            def get_field(self, f_name):
                if f_name in self.fields:
                    return self.fields[f_name]
                raise AttributeError('Field name %s not found' % f_name)

            def add_manager(self, manager):
                self.managers_map[manager.name] = manager

            def add_field(self, field):
                self.fields[field.name] = field

            def get_field_by_column_name(self, f_name):
                for field in self.fields.values():
                    if f_name in [field.name, field.db_column_name]:
                        return field
                raise AttributeError('Field name %s not found' % f_name)

        _meta = Meta(cls)
        setattr(cls, '_meta', _meta)

        _meta.db_table = utils.convert_name(cls.__name__.lower())

        has_primary_key = False

        for name, attr in cls.__dict__.items():
            if (
                isinstance(attr, (managers.BaseManager, fields.Field))
            ):
                attr.contribute_to_class(cls, name)
                if isinstance(attr, fields.IDField):
                    has_primary_key = True

        if 'objects' not in cls.__dict__:
            manager = managers.Manager()
            manager.contribute_to_class(cls, 'objects')

        if not has_primary_key:
            pk = fields.IDField()
            pk.contribute_to_class(cls, 'id')

        if hasattr(cls, '__unicode__'):
            setattr(cls, '__repr__', lambda self: '<%s: %s>' % (
                self.__class__.__name__, self.__unicode__()))

        return cls


class Model(metaclass=BaseModel):

    def __init__(self, *args, **kwargs):
        self.id = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def collection_name(cls):
        return cls._meta.db_table

    def get_fields(self):
        return {
            f.name: getattr(self, f.name)
            for f in self._meta.fields.values()
        }

    def save(self, update_fields=None):
        if update_fields is not None:
            self._update(update_fields)
        else:
            self._save()

    def delete(self):
        queries.FilterQuery(
            self.__class__,
            id=self.id
        ).delete()
        self.id = None

    def _update(self, update_fields):
        queries.UpdateQuery(
            self.__class__,
            **self._get_update_fields(
                update_fields
            )
        ).execute()

    def _save(self):
        self.id = queries.InsertQuery(
            self.__class__,
            **self.get_fields()
        ).execute().id

    def _get_update_fields(self, update_fields):
        if type(update_fields) not in [list, tuple]:
            raise AttributeError('update_fields must be list or tuple')
        return {
            k: v
            for k, v in self.get_fields().items()
            if k in update_fields + ['id']
        }
