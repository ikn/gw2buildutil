class Identified:
    def __init__ (self, ids):
        ids = (ids,) if isinstance(ids, str) else ids
        self.id_ = Identified.normalise_id(ids[0])
        self.ids = {Identified.normalise_id(id_) for id_ in ids}

    @staticmethod
    def normalise_id (id_):
        return str(id_).lower()
