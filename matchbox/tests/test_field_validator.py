import unittest


from matchbox.models import fields
from matchbox.models import field_validator


class TestFieldValidator(unittest.TestCase):
    def setUp(self):
        class TestField(fields.Field):
            allowed_attributes = list(
                field_validator.FieldValidator.ATTRIBUTES
            )
        self.f_validator = field_validator.FieldValidator(
            TestField(), {}
        )

    def test_max_length(self):
        self.f_validator.attributes = {'max_length': 10}
        value = self.f_validator.validate('test', "A" * 20)
        self.assertEqual(len(value), 10)
        self.assertEqual(value, "A" * 10)

    def test_blank(self):
        with self.assertRaises(AttributeError) as context:
            self.f_validator.validate('test', None)

        self.assertEqual(
            "Field test required value",
            str(context.exception)
        )

        self.f_validator.attributes = {'blank': True}
        value = self.f_validator.validate('test', None)

        self.assertIsNone(value)

    def test_default(self):
        self.f_validator.attributes = {'default': 10}
        value = self.f_validator.validate('test', None)

        self.assertEqual(value, 10)

        self.f_validator.attributes = {'default': []}
        value = self.f_validator.validate('test', None)
        self.assertEqual(value, [])

        self.f_validator.attributes = {'default': {}}
        value = self.f_validator.validate('test', None)
        self.assertEqual(value, {})
