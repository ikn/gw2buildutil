import abc
import os
import json
import dbm

from .. import util


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
            filtered_entities = filter_(entities)
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


class Storage (abc.ABC):
    @abc.abstractmethod
    def store_schema_version (self, version):
        pass

    @abc.abstractmethod
    def schema_version (self):
        pass

    @abc.abstractmethod
    def store_raw (self, path, result):
        pass

    @abc.abstractmethod
    def exists_raw (self, path, api_id):
        pass

    @abc.abstractmethod
    def raw (self, path, api_id):
        pass

    @abc.abstractmethod
    def clear_raw (self):
        pass

    @abc.abstractmethod
    def store (self, entity):
        pass

    @abc.abstractmethod
    def relations (self, entity_type, api_id):
        pass

    def from_api_id (self, entity_type, api_id, crawler=None):
        result = self.raw(entity_type.path(), api_id)
        relations = self.relations(entity_type, api_id)
        return entity_type(result, relations, self, crawler)

    @abc.abstractmethod
    def all_from_id (self, entity_type, id_):
        pass

    def from_id (self, entity_type, id_, filters=Filters()):
        filters += entity_type.default_filters
        entities = filters.filter_(self.all_from_id(entity_type, id_))
        if len(entities) == 1:
            return entities[0]
        elif entities:
            raise KeyError(f'not unique: {repr(id_)} - matches: '
                           f'{", ".join(repr(e.id_) + repr(e.api_id) for e in entities)}')
        else:
            raise KeyError(id_)

    @abc.abstractmethod
    def clear (self):
        pass


class FileStorage (Storage):
    _SCHEMA_VERSION_KEY = 'meta:version'

    def __init__ (self, path=None):
        if path is None:
            default_cache_path = os.path.join(os.path.expanduser('~'), '.cache')
            cache_path = os.environ.get('XDG_CACHE_HOME', default_cache_path)
            self.path = os.path.join(cache_path, 'gw2buildutil')
        else:
            self.path = path

        os.makedirs(self.path, exist_ok=True)
        self._raw_db = dbm.open(os.path.join(self.path, 'api-raw.db'), 'c')
        try:
            self._db = dbm.open(os.path.join(self.path, 'api.db'), 'c')
        except Exception:
            self._raw_db.close()

    def close (self):
        try:
            self._raw_db.close()
        finally:
            self._db.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args):
        self.close()

    def store_schema_version (self, version):
        self._raw_db[self._SCHEMA_VERSION_KEY] = version

    def schema_version (self):
        if self._SCHEMA_VERSION_KEY in self._raw_db:
            return self._raw_db[self._SCHEMA_VERSION_KEY].decode()
        else:
            return None

    def _api_id_key (self, path, api_id):
        return f'entity:{"/".join(path)}:{api_id}'

    def store_raw (self, path, result):
        self._raw_db[self._api_id_key(path, result['id'])] = json.dumps(result)

    def exists_raw (self, path, api_id):
        return self._api_id_key(path, api_id) in self._raw_db

    def raw (self, path, api_id):
        return json.loads(self._raw_db[self._api_id_key(path, api_id)])

    def clear_raw (self):
        for key in self._raw_db.keys():
            del self._raw_db[key]

    def _id_key (self, entity_type, id_):
        return (f'{entity_type.type_id()}:'
                f'id:{util.Identified.normalise_id(id_)}')

    def _store (self, entity_type, api_id, ids):
        for id_ in ids:
            id_key = self._id_key(entity_type, id_)
            if id_key in self._db:
                data = json.loads(self._db[id_key])
            else:
                data = []
            data.append(api_id)
            self._db[id_key] = json.dumps(tuple(set(data)))

    def _relations_key (self, entity_type, api_id):
        return (f'{entity_type.type_id()}:relations:{api_id}')

    def _store_relations (self, entity_type, api_id, dest_entity, ids):
        relations_key = self._relations_key(entity_type, api_id)
        dest_entity_ref = (type(dest_entity).type_id(), dest_entity.api_id)
        if relations_key in self._db:
            data = json.loads(self._db[relations_key])
        else:
            data = {}
        relations = {id_: set([(tuple(e_type_id), ref_api_id)
                               for e_type_id, ref_api_id in refs])
                     for id_, refs in data.items()}
        for id_ in ids:
            relations.setdefault(id_, set()).add(dest_entity_ref)
        data_out = {id_: list(refs) for id_, refs in relations.items()}
        self._db[relations_key] = json.dumps(data_out)

    def store (self, entity):
        self._store(type(entity), entity.api_id, entity.ids)

        for (other_type, other_api_id), relation_ids \
            in entity.extra_entity_relations().items() \
        :
            self._store_relations(
                other_type, other_api_id, entity, relation_ids)

    def relations (self, entity_type, api_id):
        relations_key = self._relations_key(entity_type, api_id)
        if relations_key in self._db:
            relations_data = json.loads(self._db[relations_key])
        else:
            relations_data = {}
        return Relations({
            name: [Relation(e_type_id, api_id) for (e_type_id, api_id) in rs]
            for name, rs in relations_data.items()})

    def all_from_id (self, entity_type, id_):
        key = self._id_key(entity_type, id_)
        api_ids = json.loads(self._db[key])
        return [self.from_api_id(entity_type, api_id) for api_id in api_ids]

    def clear (self):
        for key in self._db.keys():
            del self._db[key]


class CrawlingStorage (Storage):
    def __init__ (self, storage, crawler):
        self._storage = storage
        self._crawler = crawler

    def store_schema_version (self, version):
        self._storage.store_schema_version(version)

    def schema_version (self):
        return self._storage.schema_version()

    def store_raw (self, path, result):
        self._storage.store_raw(path, result)

    def exists_raw (self, path, api_id):
        return self._storage.exists_raw(path, api_id)

    def raw (self, path, api_id):
        self._crawler.crawl_raw(path, (api_id,))
        return self._storage.raw(path, api_id)

    def clear_raw (self):
        self._storage.clear_raw()

    def store (self, entity):
        self._storage.store(entity)

    def relations (self, entity_type, api_id):
        return self._storage.relations(entity_type, api_id)

    def all_from_id (self, entity_type, id_):
        return self._storage.all_from_id(entity_type, id_)

    def clear (self):
        self._storage.clear()
