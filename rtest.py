import os

from matchbox import models
from matchbox.database import db_initialization

db_initialization(os.environ['FIRESTORE'])

print("Test Model.")


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


Class.objects.delete()


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


Class2.objects.delete()



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

NewClass.objects.delete()


print("Test ref model")


class A(models.Model):
    name = models.TextField()


class B(models.Model):
    name = models.TextField()


class NewBaseClass(models.Model):
    name = models.TextField(default='aaaaa')
    active = models.BooleanField(column_name='is_active', default=False)
    list_f = models.ListField(default=[], column_name='lista')
    map_f = models.MapField(default={}, column_name='mapa')
    ref_a = models.ReferenceField(A)

    class Meta:
        abstract = True
        collection_name = 'collection_name'


class NewClass(NewBaseClass):
    ref_b = models.ReferenceField(B)


A.objects.delete()
B.objects.delete()
NewClass.objects.delete()


a1 = A.objects.create(name='a1')
a2 = A(name='a2')
a2.save()

b1 = B.objects.create(name='b1')
b2 = B(name='b2')
b2.save()


nc1 = NewClass(ref_a=a1, name='test', active=False, list_f=[1, 2, 3])
nc1.save()

nc2 = NewClass.objects.create(
    ref_a=a2, name='test2', active=True, ref_b=b1
)


assert isinstance(nc1.ref_a, A)
assert nc1.ref_a.id == a1.id
assert nc1.ref_a.name == a1.name
assert nc1.ref_b is None


assert isinstance(nc2.ref_a, A)
assert isinstance(nc2.ref_b, B)

assert nc2.ref_a.id == a2.id
assert nc2.ref_b.name == b1.name
assert nc2.ref_b.id == b1.id


all_ncs = list(NewClass.objects.all())

for anc in all_ncs:
    assert isinstance(anc.ref_a, A) or isinstance(anc.ref_a, type(None))
    assert isinstance(anc.ref_b, B) or isinstance(anc.ref_b, type(None))


A.objects.delete()
B.objects.delete()
NewClass.objects.delete()


print("Test Sub models")

import os

from matchbox import models
from matchbox.database import db_initialization

db_initialization(os.environ['FIRESTORE'])

class A(models.Model):
    name = models.TextField()
    active = models.BooleanField()


class B(models.Model):
    name = models.TextField()
    active = models.BooleanField()


class C(models.Model):
    name = models.TextField()
    active = models.BooleanField()


a1 = A.objects.create(name='Test', active=True)
a2 = A.objects.create(name='Test2', active=True)

B.set_base_path(a1)

b1 = B.objects.create(name='B Test', active=False)
b2 = B.objects.create(name='B Test 2', active=True)


assert b1.path == ('a', a1.id, 'b')
assert b2.path == ('a', a1.id, 'b')
assert len(list(B.objects.all())) == 2


C.set_base_path(b1)
assert C.path == ('a', a1.id, 'b', b1.id, 'c')

c1 = C.objects.create(name='C Test', active=True)

C.reset_base_path()
assert C.path == ('c', )

C.reset_base_path()
C.set_base_path(b2)

assert C.path == ('a', a1.id, 'b', b2.id, 'c')

c2 = C.objects.create(name='C Test', active=False)

C.reset_base_path()
C.set_base_path(b1)

assert len(list(C.objects.all())) == 1
assert C.objects.get().id == c1.id


C.reset_base_path()
C.set_base_path(b2)

assert len(list(C.objects.all())) == 1
assert C.objects.get().id == c2.id

for a in A.objects.all():
    B.set_base_path(a)
    for b in B.objects.all():
        C.set_base_path(b)
        C.objects.delete()
    B.objects.delete()
A.objects.delete()



from matchbox import models, database
import os

database.db_initialization(os.environ['FIRESTORE'])


class User(models.Model):
    name = models.TextField()


class Message(models.Model):
    msg = models.TextField()
    user = models.ReferenceField(User)

    class Meta:
        collection_name = 'messages'


class Room(models.Model):
    name = models.TextField()

    class Meta:
        collection_name = 'rooms'


u_neo = User.objects.create(name='Neo')
u_matrix = User.objects.create(name='Matrix')

r = Room.objects.create(name='roomA')

Message.set_base_path(r)

m1 = Message.objects.create(user=u_neo, msg='Matrix ?')
m2 = Message.objects.create(user=u_matrix, msg='Follow the white rabbit')

assert m1.user.id == u_neo.id
assert m2.user.id == u_matrix.id

m1 = Message.objects.get(id=m1.id)
m2 = Message.objects.get(id=m2.id)

assert m1.user.id == u_neo.id
assert m2.user.id == u_matrix.id

m1.delete()
m2.delete()

r.delete()
u_neo.delete()
u_matrix.delete()

