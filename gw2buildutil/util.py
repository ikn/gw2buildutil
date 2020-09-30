class Identified:
    def __init__ (self, ids, aliases=()):
        ids = (ids,) if isinstance(ids, str) else ids
        self.id_ = Identified.normalise_id(ids[0])
        self.ids = {Identified.normalise_id(id_) for id_ in ids}
        aliases = (aliases,) if isinstance(aliases, str) else aliases
        self.aliases = {Identified.normalise_id(alias) for alias in aliases}
        if self.ids & self.aliases:
            raise ValueError('IDs and aliases may overlap: '
                             f'{self.ids & self.aliases}')

    @staticmethod
    def normalise_id (id_):
        return id_.lower()
