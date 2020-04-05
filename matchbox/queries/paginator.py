from .queries_result import QueryResultWrapper


class Paginator:
    def __init__(self, query, page_count):
        self.query = query
        self.page_count = page_count
        self._res = None

    def __str__(self):
        return "Paginator {} {}".format(self.query.model, self.page_count)

    def __iter__(self):
        self.query.limit(self.page_count)
        return self

    def __next__(self):
        self.make_query(self.last_doc)
        return self.wrap_response()

    @property
    def last_doc(self):
        if not self._res:
            return
        return self._res[-1]

    def make_query(self, start_after=None):
        if start_after is not None:
            self.query.start_after(start_after)
        self._res = list(self.query.raw_execute())
        if not self._res:
            raise StopIteration

        if start_after is None:
            return

        if start_after.id == self.last_doc.id:
            raise StopIteration

    def wrap_response(self):
        return [
            QueryResultWrapper.model_from_dict(self.query.model, d)
            for d in self._res if d
        ]
