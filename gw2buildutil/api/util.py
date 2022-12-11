from . import entity


class Filter:
    def __init__ (self, filter_):
        self._filter = filter_

    def filter_ (self, entities):
        return self._filter(entities)


class TypedFilter (Filter):
    def __init__ (self, entity_type, filter_):
        self.entity_type = entity_type
        Filter.__init__(self, filter_)

    def filter_ (self, entities):
        filtered = [e for e in entities if not isinstance(e, self.entity_type)]
        filtered.extend(self._filter([e for e in entities
                                      if isinstance(e, self.entity_type)]))
        return filtered


class Filters:
    def __init__ (self, filters=()):
        self._filters = tuple(filters)

    def __add__ (self, other):
        if not isinstance(other, Filters):
            return NotImplemented
        return Filters(self._filters + other._filters)

    def filter_ (self, entities):
        for filter_ in self._filters:
            if len(entities) <= 1:
                break
            filtered_entities = filter_.filter_(entities)
            if filtered_entities:
                entities = filtered_entities
        return entities


class Relation:
    def __init__ (self, entity_type_id, api_id):
        self.entity_type_id = entity_type_id
        self.api_id = api_id

    def entity_raw (self, entity_type, storage):
        return storage.raw(entity_type.path(), self.api_id)

    def entity (self, entity_type, storage, crawler=None):
        return storage.from_api_id(entity_type, self.api_id, crawler)

    def __repr__ (self):
        return f'Relation<{self.entity_type_id} {self.api_id}>'


class Relations:
    def __init__ (self, relations):
        self._relations = relations

    def all_matching (self, name, entity_type):
        expect_type_id = entity_type.type_id()
        for relation in self._relations.get(name, ()):
            if relation.entity_type_id == expect_type_id:
                yield relation

    def matching (self, name, entity_type):
        try:
            return next(self.all_matching(name, entity_type))
        except StopIteration:
            return None

    def entities_raw (self, name, entity_type, storage):
        for relation in self.all_matching(name, entity_type):
            yield relation.entity_raw(entity_type, storage)

    def entity_raw (self, name, entity_type, storage):
        relation = self.matching(name, entity_type)
        if relation is not None:
            return relation.entity_raw(entity_type, storage)

    def entities (self, name, entity_type, storage, crawler=None):
        for relation in self.all_matching(name, entity_type):
            yield relation.entity(entity_type, storage, crawler)

    def entity (self, name, entity_type, storage, crawler=None):
        relation = self.matching(name, entity_type)
        if relation is not None:
            return relation.entity(entity_type, storage, crawler)

    def __repr__ (self):
        return f'Relations<{self._relations}>'


def lookup_profession (id_, storage):
    try:
        profession = storage.from_id(entity.Profession, id_)
        elite_spec = None
    except KeyError:
        elite_spec = storage.from_id(entity.Specialisation, id_)
        if not elite_spec.is_elite:
            raise KeyError(id_)
        profession = elite_spec.profession

    return (profession, elite_spec)
