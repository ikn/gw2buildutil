import json
import urllib.parse
import urllib.request

BASE_URL = 'https://api.guildwars2.com/v2'
SCHEMA_VERSION = '2020-10-01T00:00:00Z'
MAX_QUERYSTRING_SIZE = 1024
BATCH_SIZE = 100


class Client:
    def __init__ (self, base_url=BASE_URL, batch_size=BATCH_SIZE):
        self.base_url = base_url
        self.batch_size = batch_size

    def _url (self, path):
        path = '/'.join(urllib.parse.quote(part, safe='') for part in path)
        return f'{self.base_url}/{path}'

    def _get_json (self, url):
        req = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'X-Schema-Version': SCHEMA_VERSION,
        })
        with urllib.request.urlopen(req) as res:
            body = res.read()
        return json.loads(body)

    def list_(self, path):
        return self._get_json(self._url(path))

    def _get_batch (self, path, querystring_parts):
        url = f'{self._url(path)}?{"".join(querystring_parts)}'
        return self._get_json(url)

    def get (self, path, ids):
        sep = urllib.parse.quote_plus(',')
        sep_size = len(sep)

        querystring_parts = ['ids=']
        batch_size = 0
        querystring_size = 4
        for id_ in ids:
            id_quoted = urllib.parse.quote_plus(str(id_))
            if batch_size > 0 and (
                batch_size + 1 > BATCH_SIZE or
                querystring_size + len(id_quoted) > MAX_QUERYSTRING_SIZE
            ):
                yield from self._get_batch(path, querystring_parts)
                querystring_parts = ['ids=']
                batch_size = 0
                querystring_size = 4
            querystring_parts.append(sep)
            querystring_parts.append(id_quoted)
            batch_size += 1
            querystring_size += sep_size + len(id_quoted)

        if batch_size > 0:
            yield from self._get_batch(path, querystring_parts)
