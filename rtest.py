import os

from matchbox import models
from matchbox.database import db_initialization

db_initialization(os.environ['FIRESTORE'])


class Class(models.Model):
    name = models.TextField()
    active = models.BooleanField(column_name='is_active')
    list_f = models.ListField(blank=True)
    map_f = models.MapField(blank=True)


Class.objects.delete()


c1 = Class.objects.create(active=True, name='DD21')
c2 = Class.objects.create(active=True, name='DD22')
c3 = Class.objects.create(active=False, name='CC22')
c4 = Class.objects.create(active=False, name='CC11')


assert len(list(Class.objects.all())) == 4
assert len(list(Class.objects.filter(active=True))) == 2
assert len(list(Class.objects.filter(active=False))) == 2


assert len(list(Class.objects.filter(active=True).filter(name='DD21'))) == 1
assert len(list(Class.objects.filter(active=True).filter(name='DD22'))) == 1

assert len(list(Class.objects.filter(active=False).filter(name='CC22'))) == 1
assert len(list(Class.objects.filter(active=False).filter(name='CC11'))) == 1


class BaseClass(models.Model):
    name = models.TextField()
    active = models.BooleanField(column_name='is_active')
    list_f = models.ListField(blank=True, column_name='lista')

    class Meta:
        abstract = True
        collection_name = 'collection_name'


class Class2(BaseClass):
    map_f = models.MapField(blank=True, column_name='mapa')


Class2.objects.delete()


assert BaseClass._meta.abstract, True
assert BaseClass.collection_name(), 'collection_name'

assert Class2.collection_name(), 'class'
assert not Class2._meta.abstract


Class2.objects.create(
    name='DDDD',
    active=False,
    map_f={'key': 'val'}
)


assert len(list(Class2.objects.filter(map_f__key='val'))) == 1
assert not len(list(Class2.objects.filter(map_f__key='val1')))

c1 = Class2.objects.filter(map_f__key='val').get()
c1.list_f = [1, 2, 3]
c1.save()


c1 = Class2.objects.get(id=c1.id)
assert c1.list_f, [1, 2, 3]


class NewBaseClass(models.Model):
    name = models.TextField(default='aaaaa')
    active = models.BooleanField(column_name='is_active', default=False)
    list_f = models.ListField(default=[], column_name='lista')
    map_f = models.MapField(default={}, column_name='mapa')

    class Meta:
        abstract = True
        collection_name = 'collection_name'


class NewClass(NewBaseClass):
    age = models.IntegerField(default=0)


NewClass.objects.delete()

NewClass.objects.create()

assert len(list(NewClass.objects.all())) == 1
last_nc = list(NewClass.objects.all())[0]

print(type(last_nc.list_f), last_nc.list_f, isinstance(last_nc.list_f, list))
assert isinstance(last_nc.list_f, list) is True
assert isinstance(last_nc.name, str) is True
assert isinstance(last_nc.active, bool) is True
assert isinstance(last_nc.age, int) is True
assert isinstance(last_nc.map_f, dict) is True

assert last_nc.list_f == []
assert last_nc.name == 'aaaaa'
assert last_nc.active is False
assert last_nc.map_f == {}
assert last_nc.age == 0
