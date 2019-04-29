from firebase_admin import firestore

from matchbox.database import db
from matchbox.queries import error
from matchbox.queries import queries_result


class Query:

    def __init__(self, model):
        self.model = model

    def all(self):
        return FilterQuery(self.model)

    def filter(self, **kwargs):
        return FilterQuery(self.model, **kwargs)

    def create(self, **kwargs):
        model = self.model(**kwargs)
        model.save()
        return model

    def get(self, id):
        return GetQuery(self.model, id).execute()

    def delete(self):
        FilterQuery(self.model).delete()


class QueryBase:
    def __init__(self, model):
        self.model = model

    def get_field_cls(self, field_name):
        return self.model._meta.get_field(field_name)


class GetQuery(QueryBase):
    def __init__(self, model, _id):
        super().__init__(model)
        self.id = _id

    def make_query(self):
        return db.conn.collection(
            self.model._meta.db_table
        ).document(self.id)

    def raw_execute(self):
        return self.make_query().get()

    def execute(self):
        rq = self.raw_execute()
        if rq.exists:
            return queries_result.QueryResultWrapper.model_from_dict(
                self.model, rq
            )
        raise error.DocumentDoesNotExists(self.id)


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
            fs, o = s_fs[:-1], s_fs[-1]
            wheres.append(('.'.join(fs), self.operations[o], vl))
        return wheres

    def make_query(self):
        bsq = db.conn.collection(self.model._meta.db_table)
        if 'id' in self.select_query:
            raise Exception("Can't filter using id")
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
        DeleteQuery(bsq).execute()

    def filter(self, **kwargs):
        self.select_query.update(kwargs)
        return self

    def one(self):
        try:
            return queries_result.QueryResultWrapper.model_from_dict(
                self.model,
                next(self.make_query().stream())
            )
        except StopIteration:
            return None


class InsertQuery(QueryBase):

    def __init__(self, model, **kwargs):
        super().__init__(model)
        self.insert_query = kwargs

    def parse_insert(self):
        out = {}
        for k, v in self.insert_query.items():
            field = self.model._meta.get_field(k)
            out[k] = field.lookup_value(None, v)
        return out

    def raw_execute(self):
        kwargs = self.parse_insert()
        _id = kwargs.pop('id')
        db.conn.collection(
            self.model._meta.db_table
        ).document(
            _id
        ).set(kwargs)
        return _id

    def execute(self):
        return self.raw_execute()


class UpdateQuery(InsertQuery):

    def raw_execute(self):
        kwargs = self.parse_insert()
        _id = kwargs.pop('id')
        db.conn.collection(
            self.model._meta.db_table
        ).document(
            _id
        ).update(kwargs)
        return _id


class DeleteQuery:
    def __init__(self, query):
        self.query = query

    def delete_collection(self, batch_size):
        try:
            docs = self.query.limit(10).get()
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
        self.delete_collection(10)
