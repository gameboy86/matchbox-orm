from matchbox.queries import queries


class ManagerDescriptor:
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError(
                "Manager isn't accessible via %s instances" % cls.__name__
            )
        if cls._meta.abstract:
            raise AttributeError(
                "Manager isn't accessible via %s abstract model" % cls.__name__
            )
        return cls._meta.managers_map[self.manager.name]


class BaseManager:
    def __init__(self):
        self.model = None
        self.name = None

    def contribute_to_class(self, model, name):
        self.name = self.name or name
        self.model = model
        setattr(model, name, ManagerDescriptor(self))
        model._meta.add_manager(self)

    def get_queryset(self):
        return queries.QuerySet(self.model)

    def all(self):
        return self.get_queryset().filter()

    def filter(self, **kwargs):
        return self.get_queryset().filter(**kwargs)

    def create(self, **kwargs):
        return self.get_queryset().create(**kwargs)

    def get(self, **kwargs):
        return self.get_queryset().get(**kwargs)

    def delete(self):
        self.get_queryset().delete()


class Manager(BaseManager):
    pass

