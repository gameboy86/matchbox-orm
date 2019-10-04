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

    def test_full_collection_name(self):
        class TestModelClassParent(models.Model):
            name = models.TextField()
            age = models.IntegerField()

        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                collection_name = 'tmc'

        tmcp = TestModelClassParent()
        tmcp.id = 'AEX123123'

        TestModelClass.set_base_path(tmcp)

        self.assertEqual(TestModelClassParent.full_collection_name(), 'test_model_class_parent')
        self.assertEqual(TestModelClass.full_collection_name(), 'test_model_class_parent/AEX123123/tmc')

    def test_path(self):
        class TestModelClassParent(models.Model):
            name = models.TextField()
            age = models.IntegerField()

        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                collection_name = 'tmc'

        tmcp = TestModelClassParent()
        tmc = TestModelClass()

        self.assertEqual(tmcp.path, ('test_model_class_parent',))
        self.assertEqual(tmc.path, ('tmc', ))

    def test_model_path(self):
        class TestModelClassParent(models.Model):
            name = models.TextField()
            age = models.IntegerField()

        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                collection_name = 'tmc'

        tmcp = TestModelClassParent()
        tmcp.id = 'AEX123123'

        tmc = TestModelClass()

        self.assertEqual(
            tmcp.model_path,
            ('test_model_class_parent', 'AEX123123')
        )

        self.assertEqual(
            tmc.model_path,
            ('tmc', None)
        )

    def test_set_base_path(self):
        class TestModelClassParent(models.Model):
            name = models.TextField()
            age = models.IntegerField()

        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                collection_name = 'tmc'

        tmcp = TestModelClassParent()
        tmcp.id = 'AEX123123'

        TestModelClass.set_base_path(tmcp)
        self.assertEqual(
            TestModelClass.path,
            ('test_model_class_parent', 'AEX123123', 'tmc')
        )

    def test_set_base_path_no_id(self):
        class TestModelClassParent(models.Model):
            name = models.TextField()
            age = models.IntegerField()

        class TestModelClass(models.Model):
            name = models.TextField()
            age = models.IntegerField()

            class Meta:
                collection_name = 'tmc'

        tmcp = TestModelClassParent()

        with self.assertRaises(AttributeError) as context:
            TestModelClass.set_base_path(tmcp)

        self.assertEqual(
            "You can't set base path if parent instance has "
            "not been saved (don't have id)",
            str(context.exception)
        )
