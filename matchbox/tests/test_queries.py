import unittest

from matchbox.queries.queries import FilterQuery
from matchbox.models import models


class TestFilterQuery(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_where(self):
        class TestModel(models.Model):
            pass

        bsq = FilterQuery(TestModel)
        self.assertFalse(bsq.parse_where())
        bsq = FilterQuery(TestModel, test=10)
        pq = bsq.parse_where()
        self.assertEqual(len(pq), 1)
        self.assertEqual(pq[0][0], 'test')
        self.assertEqual(pq[0][1], '==')
        self.assertEqual(pq[0][2], 10)class TestProxProviderApi(unittest.TestCase):
    def setUp(self):
        pass

    def test_registry_provider(self):
        class TestProvider(ProxProviderModelBase):
            """TEST DOC"""
            def proxies(self):
                return ['192.168.1.1:8081']

        name = convert_name(TestProvider.__name__)
        self.assertTrue(name in ProxProviderApi.available_providers())
        pro = next(
            (
                d for d in ProxProviderApi.imported_providers()
                if d['name'] == name
            ),
            None
        )

        self.assertEqual(pro['doc'], 'TEST DOC')


        pq = FilterQuery(
            TestModel, test=10, id='AEX12'
        ).filter(ar__contains=20).parse_where()

        self.assertEqual(len(pq), 3)
        q1 = pq[0]
        q2 = pq[1]
        q3 = pq[2]

        self.assertEqual(q1[0], 'test')
        self.assertEqual(q1[1], '==')
        self.assertEqual(q1[2], 10)

        self.assertEqual(q2[0], 'id')
        self.assertEqual(q2[1], '==')
        self.assertEqual(q2[2], 'AEX12')

        self.assertEqual(q3[0], 'ar')
        self.assertEqual(q3[1], 'array_contains')
        self.assertEqual(q3[2], 20)

