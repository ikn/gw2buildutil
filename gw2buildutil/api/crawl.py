import logging

from . import client as gw2client, entity as gw2entity, storage as gw2storage

logger = logging.getLogger(__name__)


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
        self.storage = gw2storage.CrawlingStorage(storage, self)
        self.entity_types = entity_types

    def crawl_raw (self, path, api_ids):
        new_api_ids = [api_id for api_id in api_ids
                       if not self.storage.exists_raw(path, api_id)]
        if not new_api_ids:
            return
        logger.info(f'get {len(new_api_ids)}/{len(api_ids)} /{"/".join(path)}')

        for result in self.client.get(path, new_api_ids):
            self.storage.store_raw(path, result)

    def _process (self, api_ids, entity_types):
        for api_id in api_ids:
            for entity_type in entity_types:
                try:
                    entity = self.storage.from_api_id(entity_type, api_id, self)
                except gw2entity.SkipEntityError:
                    pass
                else:
                    self.storage.store(entity)

    def crawl (self, entity_type, api_ids):
        self.crawl_raw(entity_type, api_ids)
        self._process(api_ids, (entity_type,))

    def crawl_all (self, entity_types):
        by_path = {}
        for entity_type in entity_types:
            by_path.setdefault(entity_type.path(), []).append(entity_type)

        ordered = list(_dependency_order(entity_types))
        ordered_grouped = sorted(by_path.values(),
                                 key=lambda group: ordered.index(group[0]))

        api_ids_by_path = {}
        for group in ordered_grouped:
            path = group[0].path()
            logger.info(f'list /{"/".join(path)}')
            api_ids = self.client.list_(path)
            api_ids_by_path[path] = api_ids
            self.crawl_raw(path, api_ids)
            self._process(api_ids, group)
        # now relations should all exist, we process again so that ID generation
        # can use relations
        for group in ordered_grouped:
            path = group[0].path()
            api_ids = api_ids_by_path[path]
            self._process(api_ids, group)


def crawl (client=gw2client.Client(),
           storage=None,
           entity_types=gw2entity.BUILTIN_TYPES,
           full_recrawl=False):
    if storage is None:
        with gw2storage.FileStorage() as storage:
            crawl(client, storage, entity_types)
        return

    crawler = Crawler(client, storage, entity_types)
    if storage.schema_version() != gw2client.SCHEMA_VERSION or full_recrawl:
        storage.clear_raw()
        storage.store_schema_version(gw2client.SCHEMA_VERSION)
    storage.clear() # required if entity definition changes
    crawler.crawl_all(entity_types)
