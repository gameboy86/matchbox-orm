from matchbox.models import utils
from matchbox.models import fields
from matchbox.models import managers


class BaseModel(type):
    def __new__(mcs, name, base, attrs):
        cls = super().__new__(mcs, name, base, attrs)

        if 'Meta' not in attrs:
            cls.Meta = None

        class Meta:
            fields = {}
            managers_map = {}

            def __init__(self, model_class):
                self.model_class = model_class
                self.collection_name = utils.convert_name(
                    cls.__name__
                )
                self.abstract = False

            def get_id_field_name(self):
                for _name, field in self.fields.items():
                    if isinstance(field, fields.IDField):
                        return _name

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

            def set_from_model_meta(self, model_meta):
                for m_name, m_val in model_meta.__dict__.items():
                    if m_name == 'collection_name':
                        self.collection_name = m_val
                    if m_name == 'abstract':
                        self.abstract = m_val

        _meta = Meta(cls)
        setattr(cls, '_meta', _meta)

        for bc in base:
            if not bc._meta.abstract:
                if bc != Model:
                    raise AttributeError(
                        "Can't inherit from non abstract class"
                    )
                continue

            for name, attr in bc._meta.fields.items():
                if isinstance(attr, fields.IDField):
                    continue
                attr.contribute_to_class(cls, name)

        for name, attr in cls.__dict__.items():
            if (
                isinstance(attr, type) and name == 'Meta'
            ):
                _meta.set_from_model_meta(attr)
            if (
                isinstance(attr, (managers.BaseManager, fields.Field))
            ):
                if isinstance(attr, fields.IDField):
                    raise AttributeError(
                        "Manually added IDField is forbidden."
                        "It will be created automatic"
                    )
                attr.contribute_to_class(cls, name)

        if 'objects' not in cls.__dict__:
            manager = managers.Manager()
            manager.contribute_to_class(cls, 'objects')

        if hasattr(cls, '__unicode__'):
            setattr(cls, '__repr__', lambda self: '<%s: %s>' % (
                self.__class__.__name__, self.__unicode__()))

        if _meta.abstract:
            return cls

        pk = fields.IDField()
        pk.contribute_to_class(cls, 'id')

        setattr(cls, 'path', (cls._meta.collection_name, ))

        return cls


class Model(metaclass=BaseModel):

    def __init__(self, *args, **kwargs):
        if self._meta.abstract:
            raise AttributeError(
                "Can't create instance of abstract Model"
            )
        self.id = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def collection_name(cls):
        return cls._meta.collection_name

    @classmethod
    def get_field(cls, name):
        return cls._meta.get_field(name)

    def get_fields(self):
        return {
            f.name: getattr(self, f.name)
            for f in self._meta.fields.values()
        }

    @classmethod
    def set_base_path(cls, model_object):
        if len([
            x for x in model_object.model_path
            if x is not None]
        ) % 2 != 0:
            raise AttributeError(
                "You can't set base path if parent instance has "
                "not been saved (don't have id)"
            )
        cls.path = model_object.model_path + (cls.collection_name(), )

    @classmethod
    def reset_base_path(cls):
        cls.path = (cls.collection_name(), )

    @property
    def model_path(self):
        return self.path + (self.id, )

    def save(self, update_fields=None):
        if update_fields is not None:
            self._update(update_fields)
        else:
            self._save()

    def delete(self):
        self.__class__.objects.delete(
            id=self.id
        )
        self.id = None

    def _update(self, update_fields):
        self.__class__.objects.update(
            **self._get_update_fields(
                update_fields
            ))

    def _save(self):
        self.id = self.__class__.objects.create(
            **self.get_fields()
        ).id

    def _get_update_fields(self, update_fields):
        if type(update_fields) not in [list, tuple]:
            raise AttributeError('update_fields must be list or tuple')
        return {
            k: v
            for k, v in self.get_fields().items()
            if k in update_fields + ['id']
        }
