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
            entities = filter_(entities)
        return entities


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
    def from_api_id (self, entity_type, api_id):
        pass

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
                           f'{", ".join(repr(e.id_) for e in entities)}')
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

    def store (self, entity):
        entity_type = type(entity)

        for id_ in entity.ids:
            id_key = self._id_key(entity_type, id_)
            if id_key in self._db:
                data = json.loads(self._db[id_key])
            else:
                data = []
            data.append(entity.api_id)
            self._db[id_key] = json.dumps(tuple(set(data)))

    def from_api_id (self, entity_type, api_id):
        return entity_type(self.raw(entity_type.path(), api_id), self, None)

    def all_from_id (self, entity_type, id_):
        key = self._id_key(entity_type, id_)
        api_ids = json.loads(self._db[key])
        return [self.from_api_id(entity_type, api_id) for api_id in api_ids]

    def clear (self):
        for key in self._db.keys():
            del self._db[key]
