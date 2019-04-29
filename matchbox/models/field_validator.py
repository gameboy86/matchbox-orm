class FieldValidator:

    ATTRIBUTES = {
        'blank',
        'max_length',
        'default'
    }

    def __init__(self, field, attributes=None):
        self.field = field
        self.attributes = attributes or {}

    @property
    def default(self):
        return self.attributes.get('default')

    def validate(self, f_name, value):
        for attr in self.attributes:
            if attr not in self.ATTRIBUTES:
                raise AttributeError('Attribute {} not recognize'.format(attr))
            if attr not in self.field.allowed_attributes:
                raise AttributeError(
                    '{} not allow attribute {}'.format(
                        self.field.__class__.__name__, attr
                    )
                )

        if self.default and value is None:
            value = self.default

        if not self.attributes.get('blank') and value is None:
            raise AttributeError('Field {} required value'.format(f_name))

        if self.attributes.get('max_length'):
            value = value[:self.attributes.get('max_length')]
        return value
