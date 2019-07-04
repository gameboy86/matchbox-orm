## Matchbox

<img src="https://i.imgur.com/nvYOAmX.png" width="300">

<br/>

| Details    | Matchbox is orm package for Google Firestore.  |
| -------    | ------                                         |
| Repository | https://github.com/gameboy86/matchbox          |
| Author     | Maciej Gębarski (https://github.com/gameboy86) |
| Contact    | mgebarski@gmail.com                            |
| License    | MIT License                                    |
| Version    | 0.2                                            |
## Details

`Matchbox` is a Python Object-Relational Mapper for Google Firestore.
It is in development.


### Installing

```bash
 pip install matchbox-orm
 ```

## Usage


### Connect to Firestore

More info, how to generate JSON file with private key you will find on [Get started with Cloud Firestore](https://firebase.google.com/docs/firestore/quickstart)

```python
from matchbox import database

database.db_initialization('path/to/serviceAccount.json')
```

### Model

#### Create

```python
from matchbox import models

class Test(models.Model):
    age = models.IntegerField()
    name = models.TextField()

    def __unicode__(self):
        return self.id
```

```python
>> t = Test()
>> print(t)
<Test: e7aad1ec1aa449d2b53b7ca8f2853ea0>
```

By default all fields are required (except `IDField`, `ReferenceField`). 
This behavior can be change using attributes `blank` or `default`. 

If we now save model we get:

```python
>> t.save()
AttributeError: Field age required value
>> t.age = 18
>> t.save()
AttributeError: Field name required value
>> t.name = 'Name'
>> t.save()
```

Another way to create model is use manager `create` method:

```python
>> Test.objects.create(name='Test', age=29)
<Test: 33eba5fd53244e38aa1b4951f104ec3c>
```

By default collection name in DB will be create based on model name. If you 
want to change it, you can do it using Meta. For example:

```python
from matchbox import models

class Test(models.Model):
    age = models.IntegerField()
    name = models.TextField()
    
    class Meta:
        collection_name = 'TestCollection'
    
    def __unicode__(self):
        return self.id
```

```python
>> Test._meta.collection_name
'TestCollection'
```

#### Update


Document can be update by two ways: override or update. 
Example below will override whole document:

```python
>> t = Test.objects.get(id='eba5fd53244e38aa1b4951f104ec3c')
>> t.age = 53
>> t.save()
```

If we want update only specific fields, we can use `update_fields` parameter in
`save` method:

```python
>> t = Test.objects.get(id='eba5fd53244e38aa1b4951f104ec3c')
>> t.age = 32
>> t.save(update_fields=['age'])
```

#### Fields


**Available fields:**
 * IDField
 * IntegerField
 * TextField
 * TimeStampField
 * BooleanField
 * ListField
 * MapField
 * GeoPointField
 * ReferenceField

#### Attributes


**Available attributes for all fields:**
 * blank (If True empty fields will save null in DB.)
 * default (If field is empty, on the save, default value will be used)
 * column_name (Name of field in DB. If empty, name of field will be used)
 

`TextField` accept on more attribute `max-length`.

```python
class Test2(models.Model):
    age = models.IntegerField(default=25)
    name = models.TextField(blank=True)
```

```python
>> t = Test2()
>> t.save()
>> t = Test2.objects.get(id=t.id)
>> print(t.age, t.name)
25 None
```

#### IDField

`IDField` is create automatically by orm. We `can't` add own, because Firestore doesn't 
allow for self named id field.

```python
>> t._meta.fields
{
    'age': <matchbox.models.fields.IntegerField at 0x111723f98>,
    'name': <matchbox.models.fields.TextField at 0x111723b70>,
    'id': <matchbox.models.fields.IDField at 0x1117232b0>
}
```

If you want you can specify your own id:

```python
>> t = Test(age=33, name='test', id='My OWN ID')
>> t.save()
>> t.id
'My OWN ID'
```

If you change id and save, new document will be create in Firestore.


#### TimeStampField

```python
class TimeStampFieldExample(models.Model):
    datetimestamp = models.TimeStampField()
    
    def __unicode__(self):
        return self.id
```
```python
>> TimeStampFieldExample.objects.create(datetimestamp=datetime.datetime.now())
<TimeStampFieldExample: xp4LHczLwzcpC8Q4yF5s>

>> list(TimeStampFieldExample.objects.filter(datetimestamp__lte=datetime.datetime.now()))
[<TimeStampFieldExample: xp4LHczLwzcpC8Q4yF5s>]

>> TimeStampFieldExample.objects.filter(datetimestamp__lte=datetime.datetime.now()).get().datetimestamp
datetime.datetime(2019, 5, 4, 16, 42, 34, 583953, tzinfo=datetime.timezone(datetime.timedelta(0), '+00:00'))
```

#### ListField

```python
class ListFieldExample(models.Model):
    list_f = models.ListField()

    def __unicode__(self):
        return self.id
```

```python
>> ListFieldExample.objects.create(list_f=[1, 2, 3, 4, 5])
>> list(ListFieldExample.objects.filter(list_f__contains=5))
[<ListFieldExample: vZvDWm2EG6Di1wm85uD8>]

>> ListFieldExample.objects.filter(list_f__contains=5).get().list_f
[1, 2, 3, 4, 5]
```

#### MapField

```python
class MapFieldExample(models.Model):
    map_f = models.MapField()

    def __unicode__(self):
        return self.id
```

```python
>> MapFieldExample.objects.create(map_f = {'a': 1, 'b': 2, 'c': {'a': 1}})
<MapFieldExample: JVggchyQn19knDfx2SNX>

>> list(MapFieldExample.objects.filter(map_f__c__a=1))
[<MapFieldExample: JVggchyQn19knDfx2SNX>]

>> list(MapFieldExample.objects.filter(map_f__c__a=1))[0].map_f
{'b': 2, 'c': {'a': 1}, 'a': 1}
```

#### GeoPointField


To save GeoPoint data you must use class `GeoPointValue`

```python
class GeoPointFieldExample(models.Model):
    geo_point_f = models.GeoPointField()
    
    def __unicode__(self):
        return self.id
```

```python 
>> gpf = GeoPointFieldExample()
>> gpf.geo_point_f = GeoPointValue(latitude=52.2297, longitude=21.0122)
>> gpf.save()

>> list(GeoPointFieldExample.objects.all())[0].geo_point_f
<matchbox.models.utils.GeoPointValue at 0x11191da58>

>> list(GeoPointFieldExample.objects.all())[0].geo_point_f.latitude
52.2297
```

#### ReferenceField


One of field offered by FireStore is Reference. In one document you can store
reference to another document.

```python

class User(models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.id

class Class(models.Model):
    name = models.TextField()
    user = models.ReferenceField(User)
    
    def __unicode__(self):
        return self.id
```

```python
>> u = User.objects.create(name='Alex')
>> c = Class.objects.create(name='A1', user=u)
>> c.user
<User: cdda43cf3d65413f9eea17349e8222b8>

>> c.user.id, c.user.name
('cdda43cf3d65413f9eea17349e8222b8', 'Alex')

```

#### Query


##### objects.get

```python
    class User(models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.id
```

```python
>> u = User.objects.create(name='Alex')
>> User.objects.get(id=u.id)
<User: fe500b4bc341471fa3118854b705c674>
```


##### objects.all


Return all documents in collection

```python
class User(models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.id

class Class(models.Model):
    name = models.TextField()
    user = models.ReferenceField(User)
    
    def __unicode__(self):
        return self.id
```

```python
>> User.objects.create(name='Tom')
>> User.objects.create(name='Alex')
>> User.objects.create(name='Michael')
>> User.objects.all()
<matchbox.queries.queries.FilterQuery at 0x1116a3978>

>> list(User.objects.all())
[<User: 6b8e2190ebe3428e8c30433e74287639>,
<User: 96767fdc81ba48779683868d2a81cbba>,
<User: fe500b4bc341471fa3118854b705c674>]
```

##### objects.filter

Filter is based on django filter method. FireStore allow following comparison, 
with are mapped to:

| FireStore | Matchbox |
| --------  | -------- |
|    `<`    | lt       |
|   `<=`    | lte      |
|   `>`     | gt       |
|   `>=`    | gte      |
|   `==`    | not need |
|   `array_contains` | contains|


```python
class User(models.Model):
    name = models.TextField()
    evaluations = models.ListField()
    age = models.IntegerField(default=20)
    
    def __unicode__(self):
       return self.id

```

```python
>> User.objects.create(name='Tom', evaluations=[1,1,2], age=15)
>> User.objects.create(name='Michael', evaluations=[2,3,5])
>> User.objects.create(name='Michael', evaluations=[4,4,2])
>> User.objects.filter()
[<User: 2dce37628c4345b0a9d1a721265984b4>,
<User: 348bf6888d1e4d22afd29385f8c1a330>,
<User: 389ac1ca88614d5fa5e53facb1249576>]

>> User.objects.filter(age__gte=10, age__lte=15)
[<User: 348bf6888d1e4d22afd29385f8c1a330>]

>> u = User.objects.filter(age__gte=10, age__lte=15).get()
>> print(u.age)
15

>> list(User.objects.filter(name='Michael'))
[<User: 2dce37628c4345b0a9d1a721265984b4>,
<User: 389ac1ca88614d5fa5e53facb1249576>]

>> list(User.objects.filter(name='Michael').filter(evaluations=[4,4,2])) # or list(User.objects.filter(name='Michael', evaluations=[4,4,2]))
[<User: 2dce37628c4345b0a9d1a721265984b4>]

>> u = User.objects.filter(name='Michael', evaluations=[4,4,2]).get()
>> print(u.id, u.age, u.name, u.evaluations)
2dce37628c4345b0a9d1a721265984b4 20 Michael [4, 4, 2]

>> list(User.objects.filter(evaluations__contains=3))
[<User: 389ac1ca88614d5fa5e53facb1249576>]

>> u = User.objects.filter(evaluations__contains=3).get()
>> u.id, u.name, u.evaluations
('389ac1ca88614d5fa5e53facb1249576', 'Michael', [2, 3, 5])
```

You can also filter by ReferenceField

```python
class Class(models.Model):
    name = models.TextField()
    user = models.ReferenceField(User)
    
    def __unicode__(self):
        return self.id
```

```python
>> c = Class.objects.create(name='A1', user=User.objects.all().get())
>> c.user.id, c.user.name
'2dce37628c4345b0a9d1a721265984b4', 'Michael'

>> Class.objects.filter(user=u).get()
<Class: c3728ca35d25414794f6071d3acb3e2b>
```

`order_by` and `limit`

```python

>> [(u.age, u.name) for u in User.objects.all()]
[(20, 'Michael'), (15, 'Tom'), (20, 'Michael')]

>> [(u.age, u.name) for u in User.objects.all().order_by('age')]
[(15, 'Tom'), (20, 'Michael'), (20, 'Michael')]

>> [(u.age, u.name) for u in User.objects.all().order_by('-age')]
[(20, 'Michael'), (20, 'Michael'), (15, 'Tom')]

>> [(u.age, u.name) for u in User.objects.all().order_by('-age').limit(2)]
[(20, 'Michael'), (20, 'Michael')]
```

#### Delete


We can delete document by instance or by filter.

```python
>> u = User.objects.all().get()
>> u.delete()

>> User.objects.filter(name='Alex').delete()
```

Delete whole collection:
```python
>> User.objects.delete()
or
>> User.objects.filter().delete()
```


#### Managers


Like in Django we can create own `Managers`. For example:

```python

class User(models.Model):
    name = models.TextField()
    evaluations = models.ListField()
    age = models.IntegerField(default=20)

    def __unicode__(self):
        return self.id

class AManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class DManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=False)


class Class(models.Model):
    name = models.TextField()
    user = models.ReferenceField(User)
    active = models.BooleanField()
    
    a_objects = AManager()
    f_objects = DManager()
    
    def __unicode__(self):
        return self.id
```

```python
>> c1 = Class.objects.create(active=True, name='DD21')
>> c2 = Class.objects.create(active=True, name='DD22')
>> c3 = Class.objects.create(active=False, name='CC22')
>> c4 = Class.objects.create(active=False, name='CC11')
>> list(Class.objects.all())
[<Class: 96Ww50qJVh53v46iyOPP>,
 <Class: cjGlGWM8RiJqcAQLGvXK>,
 <Class: pgvWsXY47GrYO4Eiyp2W>,
 <Class: vHZMVjda2wNEVDmoxTe2>]

>> list(Class.f_objects.all())
[<Class: pgvWsXY47GrYO4Eiyp2W>, <Class: vHZMVjda2wNEVDmoxTe2>]

>> list(Class.a_objects.all())
[<Class: 96Ww50qJVh53v46iyOPP>, <Class: cjGlGWM8RiJqcAQLGvXK>]
```

#### Abstract model

Abstract model useful when you want to put some common information into a number of other models.
You must create base class and add abstract = True in the Meta model class.

For example:

```python
from matchbox import models as fsm, database
from datetime import datetime
database.db_initialization('xxx.json')


class SuffixFsm(fsm.Model):
    createdAt = fsm.TimeStampField()
    createdBy = fsm.TextField(max_length=30, default='')

    class Meta:
        abstract = True


class SystemMaster(SuffixFsm):
    systemName = fsm.TextField(max_length=50, default='')

```

```python
>> master = SystemMaster(
        systemName='name',
        createdAt=datetime.now(),
        createdBy='test',
    )
>> master.save()
>> master.__dict__

{'id': '9ZCOPU8KRwUB4rRVF1kZ',
 'systemName': 'name',
 'createdAt': datetime.datetime(2019, 7, 4, 21, 36, 56, 472744),
 'createdBy': 'test'}


```
