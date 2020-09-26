class Identified:
    def __init__ (self, ids, aliases=()):
        ids = (ids,) if isinstance(ids, str) else ids
        self.id_ = ids[0].lower()
        self.ids = {id_.lower() for id_ in ids}
        aliases = (aliases,) if isinstance(aliases, str) else aliases
        self.aliases = {alias.lower() for alias in aliases}
        if self.ids & self.aliases:
            raise ValueError('IDs and aliases may overlap: '
                             f'{self.ids & self.aliases}')
