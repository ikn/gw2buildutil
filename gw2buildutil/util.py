class Typed:
    def __str__ (self):
        if hasattr(self, 'name'):
            return self.name
        elif isinstance(self, Identified):
            return self.id_
        else:
            return object.__repr__(self)

    def __repr__ (self):
        s = str(self)
        if s == object.__repr__(self):
            return s
        else:
            return f'<{type(self).__name__}({str(self)})>'

    def __hash__ (self):
        return hash((type(self), self._value()))

    def __eq__ (self, other):
        return hash(other) == hash(self)


class Identified:
    def __init__ (self, ids):
        ids = (ids,) if isinstance(ids, str) else ids
        self.id_ = Identified.normalise_id(ids[0])
        self.ids = frozenset(Identified.normalise_id(id_) for id_ in ids)

    def __hash__ (self):
        return hash(self.ids)

    def __eq__ (self, other):
        return hash(other) == hash(self)

    # for Typed
    def _value (self):
        return self.id_

    @staticmethod
    def normalise_id (id_):
        return str(id_).lower()
