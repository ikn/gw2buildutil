import json
import urllib.parse
import urllib.request

from . import apiclient, fakeclient

BASE_URL = 'https://api.guildwars2.com/v2'
BATCH_SIZE = 100


class Client:
    def __init__ (self, base_url=BASE_URL, batch_size=BATCH_SIZE):
        self._fake_client = fakeclient.FakeClient()
        self._api_client = apiclient.ApiClient(base_url, batch_size)
        self.schema_version = repr((
            self._fake_client.schema_version,
            self._api_client.schema_version,
        ))

    def _choose_client (self, path):
        return (self._fake_client
                if path in fakeclient.FakeClient.supported_paths
                else self._api_client)

    def list_ (self, path):
        return self._choose_client(path).list_(path)

    def get (self, path, ids):
        return self._choose_client(path).get(path, ids)
