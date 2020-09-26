import abc
import os
import json
import dbm

from . import entity as gw2entity


class Storage (abc.ABC):
    @abc.abstractmethod
    def store_raw (self, result):
        pass

    @abc.abstractmethod
    def exists_raw (self, api_id):
        pass

    @abc.abstractmethod
    def raw (self, api_id):
        pass

    @abc.abstractmethod
    def clear_raw (self):
        pass

    @abc.abstractmethod
    def store (self, entity):
        pass

    @abc.abstractmethod
    def exists (self, entity_type, api_id):
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

    def _raw_key (self, path, api_id):
        return f'entity:{"/".join(path)}:{api_id}'

    def store_raw (self, path, result):
        self._raw_db[self._raw_key(path, result['id'])] = json.dumps(result)

    def exists_raw (self, path, api_id):
        return self._raw_key(path, api_id) in self._raw_db

    def raw (self, path, api_id):
        return json.loads(self._raw_db[self._raw_key(path, api_id)])

    def clear_raw (self):
        for key in self._raw_db.keys():
            del self._raw_db[key]

    def _id_key (self, entity_type, id_):
        return f'{entity_type.type_id()}:id:{id_.lower()}'

    def _api_id_key (self, entity_type, api_id):
        return f'{entity_type.type_id()}:api_id:{api_id}'

    def store (self, entity):
        entity_type = type(entity)
        data = json.dumps(entity.to_data())

        # use latest if conflict
        self._db[self._api_id_key(entity_type, entity.api_id)] = data

        for id_ in entity.ids:
            id_key = self._id_key(entity_type, id_)
            # use latest if conflict
            self._db[id_key] = data

        for id_ in entity.aliases:
            alias_key = self._id_key(entity_type, id_)
            # don't store if conflict
            if alias_key in self._db:
                self._db[alias_key] = ''
            else:
                self._db[alias_key] = data

    def exists (self, entity_type, api_id):
        return self._api_id_key(entity_type, api_id) in self._db

    def _from_key (self, entity_type, key):
        data = self._db[key]
        if not data: # multiple entities used the same key
            raise KeyError(key)
        return entity_type.from_data(self, json.loads(data))

    def from_id (self, entity_type, id_):
        return self._from_key(entity_type, self._id_key(entity_type, id_))

    def from_api_id (self, entity_type, api_id):
        return self._from_key(entity_type,
                              self._api_id_key(entity_type, api_id))

    def clear (self):
        for key in self._db.keys():
            del self._db[key]
