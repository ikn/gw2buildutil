from . import entity


def lookup_profession (id_, storage):
    try:
        profession = storage.from_id(entity.Profession, id_)
        elite_spec = None
    except KeyError:
        elite_spec = storage.from_id(entity.Specialisation, id_)
        if not elite_spec.is_elite:
            raise KeyError(id_)
        profession = elite_spec.profession

    return (profession, elite_spec)
