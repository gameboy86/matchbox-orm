from matchbox.models import fields
from matchbox.models import error


class QueryResultWrapper(object):
    @classmethod
    def model_from_dict(cls, model_class, row_dict):
        instance = model_class()
        for attr, value in row_dict.to_dict().items():
            field = instance._meta.get_field_by_column_name(attr)
            if isinstance(field, fields.ReferenceField):
                val = ReferenceFieldWrapper.model_from_dict(field, value)
            else:
                val = field.python_value(value)
            setattr(instance, field.name, val)
        instance.id = row_dict.id
        return instance


class ReferenceFieldWrapper(object):
    @classmethod
    def model_from_dict(cls, field, value):
        if not value:
            return None
        db_val = value.get()
        if not db_val.exists:
            raise error.ReferenceCollectionObjectDoesNotExist(
                '{}/{}'.format(
                    field.ref_model.collection_name(),
                    value.id
                )
            )
        return QueryResultWrapper.model_from_dict(
            field.ref_model, db_val
        )
