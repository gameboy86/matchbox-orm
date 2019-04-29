********
matchbox
********

.. image:: https://i.imgur.com/nvYOAmX.png
   :height: 100
   :width: 200
   :alt: alternate text


``matchbox`` is orm package for google ``Cloud Firestore``. It is in development.


Connect to Firestore
********************

.. code-block:: python

    >> from matchbox import database
    >> database.db_initialization('path/to/serviceAccount.json')


Model
*****

.. code-block:: python

    >> from matchbox.models import *
    >> class Test(models.Model):
            age = IntegerField()
            name = TextField()

            def __unicode__(self):
                return self.id

    >> print(t)
    <Test: e7aad1ec1aa449d2b53b7ca8f2853ea0>

By default all fields are required (except `IDField`, `ReferenceField`). If you now save
model you get:

.. code-block:: python

    >> t.save()
    AttributeError: Field age required value
    >> t.age = 18
    >> t.save()
    AttributeError: Field name required value
    >> t.name = 'Name'
    >> t.save()

Another way to create model is use manager method `create`:

.. code-block:: python

    >> Test.objects.create(name='Test', age=29)
    <Test: 33eba5fd53244e38aa1b4951f104ec3c>

------
Fields
------

Available fields:
 - IDField
 - IntegerField
 - TextField
 - TimeStampField
 - BooleanField
 - ListField
 - MapField
 - GeoPointField
 - ReferenceField

All fields (except `IDField`, `ReferenceField`) accept attributes `blank` and `default`.
`TextField` accept on more attribute `max-length`.

.. code-block:: python

    >> class Test2(models.Model):
            age = IntegerField(default=25)
            name = TextField(blank=True)
    >> t = Test2()
    >> t.save()
    >> t = Test2.objects.get(id=t.id)
    >> print(t.age, t.name)
    25 None

=======
IDField
=======

In our example Test model we don't specify id field. It have been added automatically:

.. code-block:: python

    >> t.id
    e7aad1ec1aa449d2b53b7ca8f2853ea0
    >> t._meta.fields
    {'age': <matchbox.models.fields.IntegerField at 0x111723f98>,
     'name': <matchbox.models.fields.TextField at 0x111723b70>,
     'id': <matchbox.models.fields.IDField at 0x1117232b0>}

If you want you can specify your own id:

.. code-block:: python

    >> t = Test(age=33, name='test', id='My OWN ID')
    >> t.save()
    'My OWN ID'

If you change id and save, new document will be create in Firestore.

==============
TimeStampField
==============

.. code-block:: python

    >> class TimeStampFieldExample(models.Model):
             datetimestamp = TimeStampField()
             def __unicode__(self):
                 return self.id

    >> TimeStampFieldExample.objects.create(datetimestamp=datetime.datetime.now())
    <TimeStampFieldExample: c82aa95ab114466997968cb0bfc3b614>
    >> tsf = TimeStampFieldExample.objects.get(id='c82aa95ab114466997968cb0bfc3b614')
    >> tsf.datetimestamp
    datetime.datetime(2019, 4, 29, 0, 29, 25, 795706, tzinfo=datetime.timezone(datetime.timedelta(0), '+00:00'))


=========
ListField
=========

.. code-block:: python

    >> class ListFieldExample(models.Model):
             list_f = ListField()

             def __unicode__(self):
                return self.id

    >> lsf = ListFieldExample.objects.create(list_f = [1,2,3,4,5])
    >> lsf.list_f
    [1, 2, 3, 4, 5]
    >> ListFieldExample.objects.get(id='608d301e720c480ebaaf4c3fc08e38f6').list_f
    [1, 2, 3, 4, 5]


=========
MapField
=========

.. code-block:: python

   >> class MapFieldExample(models.Model):
             map_f = MapField()

             def __unicode__(self):
                return self.id

    >> mfe = MapFieldExample.objects.create(map_f = {'a': 1, 'b': 2})
    >> mfe.map_f
    {'a': 1, 'b': 2}
    >> MapFieldExample.objects.get(id=mfe.id).map_f
    {'a': 1, 'b': 2}


=============
GeoPointField
=============

To save GeoPoint data you must use class `GeoPointValue`

.. code-block:: python

    >> class GeoPointField(models.Model):
             geo_point_f = GeoPointField()
    >> gpf = GeoPointValue(latitude=52.2297, longitude=21.0122)
    >> gpf.save()
    >> gpd.geo_point_f
    <matchbox.models.utils.GeoPointValue at 0x1117c9be0>



==============
ReferenceField
==============

One of field offered by FireStore is Reference. In one document you can store
reference to another document.

.. code-block:: python

    >> class User(models.Model):
             name = TextField()

             def __unicode__(self):
                 return self.id

    >> class Class(models.Model):
             name = TextField()
             user = ReferenceField(User)

            def __unicode__(self):
                return self.id

    >> u = User.objects.create(name='Alex')
    >> c = Class.objects.create(name='A1', user=u)
    >> c.user
    <User: cdda43cf3d65413f9eea17349e8222b8>
    >> c.user.id, c.user.name
    ('cdda43cf3d65413f9eea17349e8222b8', 'Alex')


-----
Query
-----

===========
objects.get
===========

objects.get only accept document id:

.. code-block:: python

    >> class User(models.Model):
             name = TextField()

             def __unicode__(self):
                 return self.id

    >> u = User.objects.create(name='Alex')
    >> User.objects.get(id=u.id)
    <User: fe500b4bc341471fa3118854b705c674>


===========
objects.all
===========

Return all documents in collection

.. code-block:: python

    >> class User(models.Model):
             name = TextField()

             def __unicode__(self):
                 return self.id

    >> class Class(models.Model):
             name = TextField()
             user = ReferenceField(User)

            def __unicode__(self):
                return self.id

    >> User.objects.create(name='Tom')
    >> User.objects.create(name='Alex')
    >> User.objects.create(name='Michael')
    >> User.objects.all()
    <matchbox.queries.queries.FilterQuery at 0x1116a3978>
    >> list(User.objects.all())
    [<User: 6b8e2190ebe3428e8c30433e74287639>,
    <User: 96767fdc81ba48779683868d2a81cbba>,
    <User: fe500b4bc341471fa3118854b705c674>]

==============
objects.filter
==============

Filter is based on django filter method. FireStore allow following comparison:
 - <
 - <=
 - <=
 - >
 - >=
 - ==
 - array_contains

you can filter on them (there are mapped to < - le, <= - lte, > - gr, >= - gte, eq - ==, contains - array_contains


.. code-block:: python

    >> class User(models.Model):
             name = TextField()
             evaluations = ListField()
             age = IntegerField(default=20)

             def __unicode__(self):
                return self.id

    >> User.objects.create(name='Tom', evaluations=[1,1,2], age=15)
    >> User.objects.create(name='Michael', evaluations=[2,3,5])
    >> User.objects.create(name='Michael', evaluations=[4,4,2])
    >> User.objects.filter()
    [<User: 2dce37628c4345b0a9d1a721265984b4>,
    <User: 348bf6888d1e4d22afd29385f8c1a330>,
    <User: 389ac1ca88614d5fa5e53facb1249576>]
    >> User.objects.filter(age__gte=10, age__lte=15)
    [<User: 348bf6888d1e4d22afd29385f8c1a330>]
    >> u = User.objects.filter(age__gte=10, age__lte=15).one()
    >> print(u.age)
    15
    >> list(User.objects.filter(name__eq='Michael'))
    [<User: 2dce37628c4345b0a9d1a721265984b4>,
    <User: 389ac1ca88614d5fa5e53facb1249576>]
    >> list(User.objects.filter(name__eq='Michael').filter(evaluations__eq=[4,4,2])) # or list(User.objects.filter(name__eq='Michael', evaluations__eq=[4,4,2]))
    [<User: 2dce37628c4345b0a9d1a721265984b4>]
    >> u = User.objects.filter(name__eq='Michael', evaluations__eq=[4,4,2]).one()
    >> print(u.id, u.age, u.name, u.evaluations)
    2dce37628c4345b0a9d1a721265984b4 20 Michael [4, 4, 2]

You can also filter by ReferenceField

.. code-block:: python

    >> class Class(models.Model):
             name = TextField()
             user = ReferenceField(User)

             def __unicode__(self):
                return self.id

    >> c = Class.objects.create(name='A1', user=User.objects.all().one())
    >> c.user.id, c.user.name
    '2dce37628c4345b0a9d1a721265984b4', 'Michael'
    >> Class.objects.filter(user__eq=u).one()
    <Class: c3728ca35d25414794f6071d3acb3e2b>


`order_by` and `limit`

.. code-block:: python

    >> [(u.age, u.name) for u in User.objects.all()]
    [(20, 'Michael'), (15, 'Tom'), (20, 'Michael')]
    >> [(u.age, u.name) for u in User.objects.all().order_by('age')]
    [(15, 'Tom'), (20, 'Michael'), (20, 'Michael')]
    >> [(u.age, u.name) for u in User.objects.all().order_by('-age')]
    [(20, 'Michael'), (20, 'Michael'), (15, 'Tom')]
    >> [(u.age, u.name) for u in User.objects.all().order_by('-age').limit(2)]
    [(20, 'Michael'), (20, 'Michael')]

------
Delete
------

We can delete document by instance or by filter.

.. code-block:: python

    >> u = User.objects.all().one()
    >> u.delete()
    >> User.objects.filter(name__eq='Alex').delete()

    Delete whole collection:

    >> User.objects.delete()
    or
    >> User.objects.filter().delete()