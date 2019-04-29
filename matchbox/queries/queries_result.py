from matchbox.models import fields
from matchbox.models import error


class QueryResultWrapper(object):
    @classmethod
    def model_from_dict(cls, model_class, row_dict):
        instance = model_class()
        for attr, value in row_dict.to_dict().items():
            if attr in instance._meta.fields:
                field = instance._meta.fields[attr]
                if isinstance(field, fields.ReferenceField):
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
                    setattr(
                        instance,
                        attr,
                        QueryResultWrapper.model_from_dict(
                            field.ref_model, db_val
                        )
                    )
                else:
                    setattr(instance, attr, field.python_value(value))
        instance.id = row_dict.id
        return instance
