import unittest

from matchbox import models


class TestModel(unittest.TestCase):
    def setUp(self):
        pass

    def test_inherit_from_non_abstract(self):
        with self.assertRaises(AttributeError) as context:

            class AClass(models.Model):
                name = models.TextField()
                age = models.IntegerField()

            class BClass(AClass):
                pass

        self.assertEqual(
            "Can't inherit from non abstract class",
            str(context.exception)
        )

    def test_abstract(self):
        class AClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                abstract = True

        class BClass(AClass):
            pass

        with self.assertRaises(AttributeError) as context:
            AClass(name='a', age=20)

        self.assertEqual(
            "Can't create instance of abstract Model",
            str(context.exception)
        )

        with self.assertRaises(AttributeError) as context:
            AClass.objects.create(name='a', age=20)

        self.assertEqual(
            "Manager isn't accessible via AClass abstract model",
            str(context.exception)
        )

        b = BClass(name='b', age=19)
        fields = b.get_fields()

        self.assertTrue(AClass._meta.abstract)
        self.assertFalse(BClass._meta.abstract)

        self.assertEqual(fields['name'], 'b')
        self.assertEqual(fields['age'], 19)
        self.assertIsNone(fields['id'])
        self.assertEqual(len(fields), 3)

    def test_collection_name(self):
        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

        self.assertEqual(TestModelClass.collection_name(), 'test_model_class')

        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                collection_name = 'ownName'

        self.assertEqual(TestModelClass.collection_name(), 'ownName')
