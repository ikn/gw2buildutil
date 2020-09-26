from . import client as gw2client, entity as gw2entity, storage as gw2storage

def _dependency_order (entity_types):
    remaining = set(entity_types)
    while remaining:
        used = set()
        for t in remaining:
            if not t.crawl_dependencies() & remaining:
                yield t
                used.add(t)
        if not used:
            yield from remaining
            break
        remaining -= used


class Crawler:
    def __init__ (self, client, storage, entity_types):
        self.client = client
        self.storage = storage
        self.entity_types = entity_types

    def _crawl (self, path, api_ids):
        new_api_ids = [api_id for api_id in api_ids
                       if not self.storage.exists_raw(path, api_id)]
        if not new_api_ids:
            return
        print(f'get {len(new_api_ids)}/{len(api_ids)} /{"/".join(path)}')

        for result in self.client.get(path, new_api_ids):
            self.storage.store_raw(path, result)

    def _process (self, path, api_ids, entity_types):
        for api_id in api_ids:
            for entity_type in entity_types:
                # if we store the same entity twice, it can conflict with itself
                if not self.storage.exists(entity_type, api_id):
                    result = self.storage.raw(path, api_id)
                    entity = entity_type.from_api(self, self.storage, result)
                    if entity is not None:
                        self.storage.store(entity)

    def crawl (self, entity_type, api_ids):
        path = entity_type.path()
        self._crawl(path, api_ids)
        self._process(path, api_ids, (entity_type,))

    def crawl_all (self, entity_types):
        by_path = {}
        for entity_type in entity_types:
            by_path.setdefault(entity_type.path(), []).append(entity_type)

        ordered = list(_dependency_order(entity_types))
        ordered_grouped = sorted(by_path.values(),
                                 key=lambda group: ordered.index(group[0]))

        for group in ordered_grouped:
            path = group[0].path()
            print(f'list /{"/".join(path)}')
            api_ids = self.client.list_(path)
            self._crawl(path, api_ids)
            self._process(path, api_ids, group)


def crawl (client=gw2client.Client(),
           storage=None,
           entity_types=gw2entity.BUILTIN_TYPES,
           full_recrawl=False):
    if storage is None:
        with gw2storage.FileStorage() as storage:
            crawl(client, storage, entity_types)
        return

    crawler = Crawler(client, storage, entity_types)
    if full_recrawl:
        storage.clear_raw()
    storage.clear() # required if entity definition changes
    crawler.crawl_all(entity_types)