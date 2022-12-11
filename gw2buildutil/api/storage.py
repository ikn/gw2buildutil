import abc
import os
import json
import dbm
import inspect

from .. import util as gw2util

from . import entity as gw2entity, util


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

    def from_id (self, entity_types, id_, filters=util.Filters()):
        if inspect.isclass(entity_types):
            entity_types = (entity_types,)

        entities = []
        for entity_type in entity_types:
            try:
                entities.extend(self.all_from_id(entity_type, id_))
            except KeyError:
                pass
        if not entities:
            raise KeyError(id_)

        filters += gw2entity.Entity.DEFAULT_FILTERS
        filtered_entities = filters.filter_(entities)
        if len(filtered_entities) == 1:
            return filtered_entities[0]
        elif filtered_entities:
            entities_message = ', '.join(
                f'{type(e).type_id()}:{e.api_id}:{repr(str(e))}'
                for e in filtered_entities)
            raise KeyError(f'not unique: {repr(id_)} - matches: '
                           f'{entities_message}')
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
                f'id:{gw2util.Identified.normalise_id(id_)}')

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
        relations = {id_: set([(e_type_id, ref_api_id)
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
        return util.Relations({
            name: [util.Relation(e_type_id, api_id)
                   for e_type_id, api_id in rs]
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
