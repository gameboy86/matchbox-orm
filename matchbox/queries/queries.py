from firebase_admin import firestore

from matchbox.database import db
from matchbox.queries import error
from matchbox.queries import queries_result


class QuerySet:

    def __init__(self, model):
        self.model = model

    def all(self):
        return FilterQuery(self.model)

    def filter(self, **kwargs):
        return FilterQuery(self.model, **kwargs)

    def get(self, **kwargs):
        return FilterQuery(self.model, **kwargs).get()

    def create(self, **kwargs):
        model = self.model(**kwargs)
        model.save()
        return model

    def delete(self):
        FilterQuery(self.model).delete()


class QueryBase:
    def __init__(self, model):
        self.model = model

    def get_ref(self):
        return db.conn.collection(self.model._meta.collection_name)


class FilterQuery(QueryBase):
    operations = {
        'lt': '<',
        'lte': '<=',
        'gt': '>',
        'gte': '>=',
        'eq': '==',
        'contains': 'array_contains',
    }
    query_separator = '__'

    def __init__(self, model, **kwargs):
        super().__init__(model)
        self.select_query = kwargs
        self.n_limit = None
        self.n_order_by = []

    def parse_where(self):
        wheres = []
        for fo, vl in self.select_query.items():
            s_fs = fo.split(self.query_separator)
            if len(s_fs) == 1 or s_fs[-1] not in self.operations:
                fs, o = s_fs, 'eq'
            else:
                fs, o = s_fs[:-1], s_fs[-1]
            wheres.append(('.'.join(fs), self.operations[o], vl))
        return wheres

    def make_query(self):
        bsq = self.get_ref()
        for w in self.parse_where():
            bsq = bsq.where(*w)
        if self.n_limit:
            bsq = bsq.limit(self.n_limit)
        if self.n_order_by:
            for fo in self.n_order_by:
                if fo[0] == '-':
                    bsq = bsq.order_by(
                        fo[1:], direction=firestore.Query.DESCENDING
                    )
                else:
                    bsq = bsq.order_by(fo)
        return bsq

    def raw_execute(self):
        return self.make_query().stream()

    def limit(self, n):
        self.n_limit = n
        return self

    def order_by(self, field):
        self.n_order_by.append(field)
        return self

    def __iter__(self):
        return self.execute()

    def execute(self):
        return iter([
            queries_result.QueryResultWrapper.model_from_dict(self.model, d)
            for d in self.raw_execute() if d
        ])

    def delete(self):
        bsq = self.make_query()
        return DeleteQuery(bsq).execute()

    def filter(self, **kwargs):
        self.select_query.update(kwargs)
        return self

    def get(self, **kwargs):
        self.select_query.update(kwargs)
        res = list(self.execute())
        if not res:
            raise error.DocumentDoesNotExists(
                '{} matching query does not exist'.format(
                    self.model.__name__
                )
            )
        if len(res) > 1:
            raise error.MultipleObjectsReturned(
                'get() returned more than one {} -- it returned {}!'.format(
                    self.model.__name__, len(res)
                )
            )
        return res[0]


class InsertQuery(QueryBase):

    def __init__(self, model, **kwargs):
        super().__init__(model)
        self.insert_query = kwargs

    def get_ref(self, id=None):

        return super().get_ref().document(id)

    def parse_insert(self):
        out = {}
        for k, f in self.model._meta.fields.items():
            val = self.insert_query.get(k)
            out[f.db_column_name] = f.lookup_value(None, val)
        return out

    def raw_execute(self):
        kwargs = self.parse_insert()
        ref = self.get_ref(kwargs.get('id'))
        kwargs['id'] = ref.id
        ref.set(kwargs)
        return self.model(**kwargs)

    def execute(self):
        return self.raw_execute()


class UpdateQuery(InsertQuery):

    def parse_insert(self):
        out = {}
        for k, v in self.insert_query.items():
            field = self.model._meta.get_field(k)
            out[field.db_column_name] = field.lookup_value(None, v)
        return out

    def raw_execute(self):
        kwargs = self.parse_insert()
        ref = self.get_ref(kwargs['id'])
        ref.update(kwargs)


class DeleteQuery:
    def __init__(self, query):
        self.query = query

    def delete_collection(self, batch_size=100):
        try:
            docs = self.query.limit(batch_size).get()
        except AttributeError:
            self.query.delete()
            return

        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return self.delete_collection(batch_size)

    def execute(self):
        self.delete_collection()
