from matchbox.queries import queries


class ManagerDescriptor:
    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError(
                "Manager isn't accessible via %s instances" % cls.__name__
            )
        return queries.Query(model=cls)
