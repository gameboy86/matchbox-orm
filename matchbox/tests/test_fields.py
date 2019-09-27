import datetime
from unittest import mock

import google
import unittest
from unittest.mock import Mock, MagicMock

import matchbox
from matchbox.models import fields
from matchbox.models import error


class TestField(unittest.TestCase):
    def test_name(self):
        field = fields.Field()
        field.name = 'test_field'

        self.assertEqual(field.db_column_name, 'test_field')

        field = fields.Field(column_name='testField')
        self.assertEqual(field.db_column_name, 'testField')


class TestIdField(unittest.TestCase):

    def test_lookup_value(self):
        field = fields.IDField()
        db_v = field.lookup_value(None, 10)
        self.assertEqual(db_v, '10')

    def test_python_value(self):
        field = fields.IDField()
        p_v = field.python_value(100)
        self.assertEqual(p_v, '100')


class TestIntegerField(unittest.TestCase):
    def test_attributes(self):
        integer_field = fields.IntegerField(
            column_name='iField', max_length=100, default=0
        )

        with self.assertRaises(AttributeError) as context:
            integer_field.lookup_value(None, None)

        self.assertEqual(
            "IntegerField not allow attribute max_length",
            str(context.exception)
        )

        integer_field = fields.IntegerField()
        integer_field.name = 'integer_field'

        with self.assertRaises(AttributeError) as context:
            integer_field.lookup_value(None, None)

        self.assertEqual(
            "Field integer_field required value",
            str(context.exception)
        )

        integer_field = fields.IntegerField(blank=True)
        integer_field.name = 'integer_field'

        db_v = integer_field.lookup_value(None, None)
        self.assertIsNone(db_v)

        integer_field = fields.IntegerField(default='Not Allowed')
        integer_field.name = 'integer_field'

        with self.assertRaises(error.DBTypeError) as context:
            integer_field.lookup_value(None, None)

        self.assertEqual(
            "IntegerField required value type <class 'int'>, "
            "get <class 'str'>",
            str(context.exception)
        )

        integer_field = fields.IntegerField(default=100)
        db_v = integer_field.lookup_value(None, None)
        self.assertEqual(db_v, 100)

        p_v = integer_field.python_value(100)
        self.assertEqual(100, p_v)

        with self.assertRaises(ValueError) as context:
            integer_field.python_value('AAAAA')

        self.assertEqual(
            "invalid literal for int() with base 10: 'AAAAA'",
            str(context.exception)
        )

    def test_lookup_value(self):
        integer_field = fields.IntegerField()

        db_v = integer_field.lookup_value(None, 100)
        self.assertEqual(db_v, 100)

    def test_python_value(self):
        integer_field = fields.IntegerField()

        p_v = integer_field.python_value(100)
        self.assertEqual(p_v, 100)


class TestTextField(unittest.TestCase):
    def test_attributes(self):
        text_field = fields.TextField(
            column_name='tField', max_length=5, default='0' * 6
        )

        db_v = text_field.lookup_value(None, None)
        self.assertEqual(db_v, '00000')

        db_v = text_field.lookup_value(None, 'Too long text for this f...')
        self.assertEqual(db_v, 'Too l')

        text_field = fields.TextField(
            column_name='tField', max_length=5, blank=True
        )

        db_v = text_field.lookup_value(None, None)
        self.assertEqual(db_v, None)

        text_field = fields.TextField()
        db_v = text_field.lookup_value(None, 1000)
        self.assertEqual(db_v, '1000')

        text_field = fields.TextField()
        db_v = text_field.lookup_value(None, True)
        self.assertEqual(db_v, 'True')

        text_field = fields.TextField()
        db_v = text_field.lookup_value(None, [1, 2, 3])
        self.assertEqual(db_v, '[1, 2, 3]')

        text_field = fields.TextField()
        db_v = text_field.lookup_value(None, {'a': 11})
        self.assertEqual(db_v, "{'a': 11}")


class TestTimeStampField(unittest.TestCase):
    def test_attributes(self):
        time_field = fields.TimeStampField(
            max_length=10,
            default=datetime.datetime(2019, 1, 1, 0, 30, 30)
        )

        with self.assertRaises(AttributeError) as context:
            time_field.lookup_value(None, None)

        self.assertEqual(
            "TimeStampField not allow attribute max_length",
            str(context.exception)
        )

        time_field = fields.TimeStampField(blank=True)

        db_v = time_field.lookup_value(None, None)
        self.assertIsNone(db_v)

        time_field = fields.TimeStampField(default='A')

        with self.assertRaises(error.DBTypeError) as context:
            time_field.lookup_value(None, None)

        self.assertEqual(
            "TimeStampField required value type <class 'datetime.datetime'>, "
            "get <class 'str'>",
            str(context.exception)
        )

        with self.assertRaises(error.DBTypeError) as context:
            time_field.lookup_value(None, [1, 2, 3])
        self.assertEqual(
            "TimeStampField required value type <class 'datetime.datetime'>, "
            "get <class 'list'>",
            str(context.exception)
        )

        db_v = time_field.lookup_value(
            None, datetime.datetime(2019, 1, 1, 0, 30, 30)
        )
        self.assertEqual(db_v, datetime.datetime(2019, 1, 1, 0, 30, 30))

        p_v = time_field.python_value(datetime.datetime(2019, 1, 1, 0, 30, 30))
        self.assertEqual(
            p_v, datetime.datetime(
                2019, 1, 1, 0, 30, 30,
                tzinfo=datetime.timezone.utc
            )
        )

        with self.assertRaises(AttributeError) as context:
            time_field.python_value('AAAA')

        self.assertEqual(
            "'str' object has no attribute 'isoformat'",
            str(context.exception)
        )


class TestBooleanField(unittest.TestCase):
    def test_attributes(self):
        b_field = fields.BooleanField(max_length=10, default=True)

        with self.assertRaises(AttributeError) as context:
            b_field.lookup_value(None, None)

        self.assertEqual(
            "BooleanField not allow attribute max_length",
            str(context.exception)
        )

        b_field = fields.BooleanField(default=True)
        v = b_field.lookup_value(None, None)
        self.assertTrue(v)

        b_field = fields.BooleanField(blank=True)
        v = b_field.lookup_value(None, None)
        self.assertIsNone(v)

        b_field = fields.BooleanField(default=True)
        v = b_field.lookup_value(None, False)
        self.assertFalse(v)

        b_field = fields.BooleanField()
        v = b_field.lookup_value(None, 0)
        self.assertFalse(v)

        b_field = fields.BooleanField()
        v = b_field.lookup_value(None, 'TEST TRUE')
        self.assertTrue(v)


class TestListField(unittest.TestCase):
    def test_attributes(self):
        l_field = fields.ListField(max_length=10, default=True)

        with self.assertRaises(AttributeError) as context:
            l_field.lookup_value(None, None)

        self.assertEqual(
            "ListField not allow attribute max_length",
            str(context.exception)
        )

        l_field = fields.ListField(default=True)

        with self.assertRaises(error.DBTypeError) as context:
            l_field.lookup_value(None, None)

        self.assertEqual(
            "ListField required value type <class 'list'>, get <class 'bool'>",
            str(context.exception)
        )

        l_field = fields.ListField()

        v = l_field.lookup_value(None, [1, 2, 3])
        self.assertEqual(v, [1, 2, 3])


class TestMapField(unittest.TestCase):
    def test_attributes(self):
        m_field = fields.MapField(max_length=10, default=True)

        with self.assertRaises(AttributeError) as context:
            m_field.lookup_value(None, None)

        self.assertEqual(
            "MapField not allow attribute max_length",
            str(context.exception)
        )

        m_field = fields.MapField(default=True)

        with self.assertRaises(error.DBTypeError) as context:
            m_field.lookup_value(None, None)

        self.assertEqual(
            "MapField required value type <class 'dict'>, get <class 'bool'>",
            str(context.exception)
        )

        m_field = fields.MapField()

        v = m_field.lookup_value(None, {'a': 1})
        self.assertEqual(v, {'a': 1})


class MockRefModel1:
    id = None

    @staticmethod
    def collection_name():
        return None


class MockRefModel2:
    pass


class MockRefModel11(MockRefModel1):
    pass


class TestReferenceField(unittest.TestCase):
    def test_lookup_value_none_returns_none(self):
        r_field = fields.ReferenceField(Mock())

        actual = r_field.lookup_value(None, None)
        self.assertEqual(None, actual)

    def test_lookup_value_not_none_returns_db_value(self):
        r_field = fields.ReferenceField(Mock())

        expected = 'db_value'
        r_field.db_value = MagicMock(return_value=expected)

        actual = r_field.lookup_value(None, 'value')
        self.assertEqual(expected, actual)

    def test_db_value_ref_model_is_not_subclass(self):
        mock_model = MockRefModel1()
        mock_ref_model = MockRefModel2()
        r_field = fields.ReferenceField(mock_ref_model.__class__)

        with self.assertRaises(error.DBTypeError) as context:
            r_field.db_value(mock_model)

        self.assertEqual(
            "ReferenceField required value type MockRefModel2, get MockRefModel1",
            str(context.exception)
        )

    def test_db_value_ref_model_is_subclass(self):
        mock_model = MockRefModel11()
        mock_ref_model = MockRefModel1()
        r_field = fields.ReferenceField(mock_ref_model.__class__)

        expected = 'real_value'
        with mock.patch('matchbox.database.Database.conn'):
            google.cloud.firestore_v1.document.DocumentReference = MagicMock(return_value=expected)
            actual = r_field.db_value(mock_model)

        self.assertEqual(expected, actual)
