class Identified:
    def __init__ (self, ids):
        ids = (ids,) if isinstance(ids, str) else ids
        self.ids = tuple(ids)

    @property
    def id_ (self):
        return self.ids[0]
