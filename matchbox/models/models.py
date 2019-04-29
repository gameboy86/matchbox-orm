from matchbox.models import utils

from matchbox.models import fields
from matchbox.queries import queries
from matchbox.models import managers


class BaseModel(type):
    def __new__(mcs, name, base, attrs):
        cls = super().__new__(mcs, name, base, attrs)

        class Meta:
            fields = {}

            def __init__(self, model_class):
                self.model_class = model_class

            def get_field(self, f_name):
                if f_name in self.fields:
                    return self.fields[f_name]
                raise AttributeError('Field name %s not found' % f_name)

        _meta = Meta(cls)
        setattr(cls, '_meta', _meta)

        _meta.db_table = utils.convert_name(cls.__name__.lower())

        has_primary_key = False
        for name, attr in cls.__dict__.items():
            if not isinstance(attr, fields.Field):
                continue
            attr.add_to_class(cls, name)
            _meta.fields[attr.name] = attr
            if isinstance(attr, fields.IDField):
                has_primary_key = True

        if not has_primary_key:
            pk = fields.IDField()
            pk.add_to_class(cls, 'id')
            _meta.fields['id'] = pk

        if hasattr(cls, '__unicode__'):
            setattr(cls, '__repr__', lambda self: '<%s: %s>' % (
                self.__class__.__name__, self.__unicode__()))

        return cls


class Model(metaclass=BaseModel):

    objects = managers.ManagerDescriptor()

    def __init__(self, *args, **kwargs):
        if 'id' not in kwargs:
            self.id = self._meta.get_field('id').random_id()
        for k, v in kwargs.items():
            setattr(self, k, v)

        for f in self._meta.fields.values():
            if f.field_validator.default and not getattr(self, f.name):
                setattr(self, f.name, f.field_validator.default)

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
        queries.DeleteQuery(
            queries.GetQuery(self.__class__, self.id).make_query()
        ).execute()
        self.id = None

    def _update(self, update_fields):
        up_fields = self._get_update_fields(update_fields)
        print(up_fields)
        queries.UpdateQuery(self.__class__, **up_fields).execute()

    def _save(self):
        queries.InsertQuery(
            self.__class__,
            **self.get_fields()
        ).execute()

    def _get_update_fields(self, update_fields):
        if type(update_fields) not in [list, tuple]:
            raise AttributeError('update_fields must be list or tuple')
        return {
            k: v
            for k, v in self.get_fields().items()
            if k in update_fields + ['id']
        }
