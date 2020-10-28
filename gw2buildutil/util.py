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


def strip_empty_lines (lines, leading=True, trailing=True, inner=None):
    in_leading = True
    empty_count = 0

    for line in lines:
        if not line:
            if not (leading and in_leading):
                empty_count += 1

        else:
            if inner == 'all' and not in_leading:
                pass
            elif inner == 'collapse' and not in_leading:
                if empty_count > 0:
                    yield ''
            else: # inner is None or in_leading
                for i in range(empty_count):
                    yield ''

            empty_count = 0
            in_leading = False
            yield line

    if not trailing:
        for i in range(empty_count):
            yield ''


def group_paragraphs (lines):
    paragraph = []
    for line in lines:
        if line:
            paragraph.append(line)
        else:
            yield paragraph
            paragraph = []
    yield paragraph
