import abc
import os
import json
import dbm

from .. import util
from . import client as gw2client, entity as gw2entity


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
    def from_id (self, entity_type, id_):
        pass

    @abc.abstractmethod
    def from_api_id (self, entity_type, api_id):
        pass

    @abc.abstractmethod
    def clear (self):
        pass


class FileStorage (Storage):
    _SCHEMA_VERSION_KEY = 'meta:version'
    _CONFLICT_VALUE = ''

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
        data = str(entity.api_id)

        for id_ in entity.ids:
            id_key = self._id_key(entity_type, id_)
            # use latest if conflict
            self._db[id_key] = data

        for id_ in entity.aliases:
            alias_key = self._id_key(entity_type, id_)
            # don't store if conflict
            if alias_key in self._db:
                if (self._db[alias_key].decode() not in
                    (self._CONFLICT_VALUE, data)
                ):
                    self._db[alias_key] = self._CONFLICT_VALUE
            else:
                self._db[alias_key] = data

    def from_api_id (self, entity_type, api_id):
        return entity_type.from_api(self.raw(entity_type.path(), api_id), self)

    def from_id (self, entity_type, id_):
        key = self._id_key(entity_type, id_)
        api_id = self._db[key].decode()
        if api_id == self._CONFLICT_VALUE:
            # multiple entities used the same key
            raise KeyError((entity_type, id_))
        return self.from_api_id(entity_type, api_id)

    def clear (self):
        for key in self._db.keys():
            del self._db[key]
