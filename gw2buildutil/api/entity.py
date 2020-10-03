import abc
import inspect
import re

from .. import build, util


class Entity (abc.ABC, util.Identified):
    def __init__ (self, api_id, ids, non_unique_ids=()):
        util.Identified.__init__ (self, ids, non_unique_ids)
        self.api_id = api_id

    def __eq__ (self, other):
        return type(self) is type(other) and self.api_id == other.api_id

    @classmethod
    def type_id (cls):
        # must not contain ':'
        return cls.__name__.lower()

    @staticmethod
    def crawl_dependencies ():
        # just a performance hint - should crawl dependencies in from_api
        return set()

    @staticmethod
    @abc.abstractmethod
    def path ():
        pass

    @staticmethod
    @abc.abstractmethod
    def from_api (result, storage, crawler=None):
        # return instance, or None to skip
        pass


class Profession (Entity):
    def __init__ (self, api_id, name, build_id, skills_build_ids):
        Entity.__init__(self, api_id, (name, build_id))
        self.name = name
        self.build_id = build_id
        self.skills_build_ids = skills_build_ids

    @staticmethod
    def path ():
        return ('professions',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        skills_build_ids = {
            api_id: build_id
            for build_id, api_id in result.get('skills_by_palette', [])}
        return Profession(
            result['id'], result['name'], result['code'], skills_build_ids)


class Specialisation (Entity):
    def __init__ (self, api_id, name, profession, is_elite):
        Entity.__init__(self, api_id, name)
        self.name = name
        self.profession = profession
        self.is_elite = is_elite

    @staticmethod
    def crawl_dependencies ():
        return set([Profession])

    @staticmethod
    def path ():
        return ('specializations',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        prof_api_id = result['profession']
        if crawler is not None:
            crawler.crawl(Profession, (prof_api_id,))
        prof = storage.from_api_id(Profession, prof_api_id)
        return Specialisation(
            result['id'], result['name'], prof, result['elite'])


class Skill (Entity):
    def __init__ (self, api_id, name, build_id, storage_build_id):
        full_id = name.lower().strip('"')
        ids = []
        id_ = full_id
        if id_.endswith('!'):
            id_ = id_[:-1]
        if ':' in id_:
            id_ = id_[id_.index(':') + 1:].strip()
        if '.' in id_:
            id_ = id_.replace('.', '') # eg. 'A.E.D.'
        if id_.startswith('summon '):
            id_ = id_[len('summon '):]

        ids = [id_]
        if full_id != id_:
            ids.append(full_id)
        if storage_build_id is not None:
            ids.append(storage_build_id)

        aliases = []
        if ' ' in id_:
            abbr = ''.join(word[0] for word in id_.split(' ') if word)
            aliases.append(abbr)
            if full_id.endswith('!'):
                aliases.append(abbr + '!')

        Entity.__init__(self, api_id, ids, aliases)
        self.name = name
        self.build_id = build_id

    @staticmethod
    def crawl_dependencies ():
        return set([Profession])

    @staticmethod
    def path ():
        return ('skills',)

    @staticmethod
    def _storage_build_id (profession, build_id):
        return f'build:{profession.api_id}:{build_id}'

    @staticmethod
    def from_api (result, storage, crawler=None):
        # NOTE: other properties:
        # professions[]
        # *type [ Weapon Heal Utility Elite Profession ]
        # *weapon_type [ None Axe ... ]
        # *slot [ Downed_# Pet Profession_# Utility Weapon_# ]
        # *categories[] [ DualWield StealthAttack ]
        # *attunement [ Fire Water Air Earth ]
        # *dual_wield [ Axe ... ] # off-hand
        if 'prev_chain' in result:
            return None

        api_id = result['id']
        prof_api_ids = result.get('professions', ())
        if len(prof_api_ids) != 1:
            return None
        if crawler is not None:
            crawler.crawl(Profession, (prof_api_ids[0],))
        prof = storage.from_api_id(Profession, prof_api_ids[0])
        build_id = prof.skills_build_ids.get(api_id)
        if build_id is None:
            storage_build_id = None
        else:
            storage_build_id = Skill._storage_build_id(prof, build_id)

        return Skill(api_id, result['name'], build_id, storage_build_id)

    @staticmethod
    def from_build_id (profession, build_id, storage):
        storage_build_id = Skill._storage_build_id(profession, build_id)
        return storage.from_id(Skill, storage_build_id)


# not obtainable through the API in any sensible way
_legend_ids = {
    'assassin': ('shiro',),
    'centaur': ('ventari',),
    'demon': ('mallyx',),
    'dwarf': ('jalis',),

    'dragon': ('glint', 'herald'),
    'renegade': ('kalla',),
}

class RevenantLegend (Entity):
    def __init__ (self, api_id, name, build_id):
        id_ = name.lower()
        ids = [id_]
        ids.extend(_legend_ids.get(id_, ()))
        ids.append(build_id)

        Entity.__init__(self, api_id, ids)
        self.name = name
        self.build_id = build_id

    @staticmethod
    def crawl_dependencies ():
        return set([Skill])

    @staticmethod
    def path ():
        return ('legends',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if crawler is not None:
            crawler.crawl(Skill, (result['swap'],))
        swap_skill = storage.from_api_id(Skill, result['swap'])
        name = swap_skill.name
        if name.startswith('Legendary '):
            name = name[len('Legendary '):]
        if name.endswith(' Stance'):
            name = name[:-len(' Stance')]

        return RevenantLegend(result['id'], name, result['code'])


class RangerPet (Entity):
    def __init__ (self, api_id, name):
        full_id = name.lower()
        id_ = full_id
        if id_.startswith('juvenile '):
            id_ = id_[len('juvenile '):]
        ids = [id_]
        if full_id != id_:
            ids.append(full_id)

        Entity.__init__(self, api_id, ids)
        self.name = name

    @staticmethod
    def path ():
        return ('pets',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        return RangerPet(result['id'], result['name'])


class Stats (Entity):
    def __init__ (self, api_id, name):
        full_id = name
        id_ = full_id
        if id_.endswith('\'s'):
            id_ = id_[:-len('\'s')]
        ids = [id_]
        if full_id != id_:
            ids.append(full_id)

        Entity.__init__(self, api_id, ids)
        self.name = name

    @staticmethod
    def path ():
        return ('itemstats',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if len(result['attributes']) < 3:
            return None
        if not result['name']:
            return None
        if result['name'].find(' and ') >= 0:
            return None

        return Stats(result['id'], result['name'])


class PvpStats (Entity):
    def __init__ (self, api_id, name):
        id_ = name.lower()
        if id_.endswith(' amulet'):
            id_ = id_[:-len(' amulet')]

        Entity.__init__(self, api_id, id_)
        self.name = name

    @staticmethod
    def path ():
        return ('pvp', 'amulets')

    @staticmethod
    def from_api (result, storage, crawler=None):
        return PvpStats(result['id'], result['name'])


sigil_pattern = re.compile(r'^'
    r'(?P<tier>\w+) Sigil of (the )?(?P<name>[\w\' ]+)'
    r'$')

class Sigil (Entity):
    def __init__ (self, api_id, name):
        match = sigil_pattern.match(name)
        if match is None:
            raise ValueError(f'unexpected sigil name format: {name}')
        fields = match.groupdict()
        tier = build.UpgradeTiers(fields['tier'].lower())
        ids = [f'{tier.value} {fields["name"]}']
        if tier == build.UpgradeTiers.SUPERIOR:
            ids.append(fields['name'])

        Entity.__init__(self, api_id, ids)
        self.name = name
        self.tier = tier

    @staticmethod
    def path ():
        return ('items',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if result['type'] != 'UpgradeComponent':
            return None
        if result['details']['type'] != 'Sigil':
            return None
        if result['name'] == 'Legendary Sigil':
            return None

        return Sigil(result['id'], result['name'])


rune_pattern = re.compile(r'^'
    r'(?P<tier>\w+) Rune of (the )?(?P<name>[\w\' ]+)'
    r'$')

class Rune (Entity):
    def __init__ (self, api_id, name):
        match = rune_pattern.match(name)
        if match is None:
            raise ValueError(f'unexpected rune name format: {name}')
        fields = match.groupdict()
        tier = build.UpgradeTiers(fields['tier'].lower())
        ids = [f'{tier.value} {fields["name"]}']
        if tier == build.UpgradeTiers.SUPERIOR:
            ids.append(fields['name'])

        Entity.__init__(self, api_id, ids)
        self.name = name
        self.tier = tier

    @staticmethod
    def path ():
        return ('items',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if result['type'] != 'UpgradeComponent':
            return None
        if result['details']['type'] != 'Rune':
            return None
        if result['name'] in ('', 'Legendary Rune'):
            return None

        return Rune(result['id'], result['name'])


food_prefixes = (
    'plate', 'bowl', 'can', 'pot', 'cup', 'jug', 'bit', 'slice', 'loaf',
    'strip', 'glass', 'handful', 'piece',
)

class Food (Entity):
    def __init__ (self, api_id, name):
        full_id = name.lower()
        aliases = []
        for prefix in food_prefixes:
            full_prefix = f'{prefix} of '
            if full_id.startswith(full_prefix):
                aliases.append(full_id[len(full_prefix):])
                break

        Entity.__init__(self, api_id, full_id, aliases)
        self.name = name

    @staticmethod
    def path ():
        return ('items',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if result['type'] != 'Consumable':
            return None
        if result['details']['type'] != 'Food':
            return None

        return Food(result['id'], result['name'])


class UtilityConsumable (Entity):
    def __init__ (self, api_id, name):
        Entity.__init__(self, api_id, name)
        self.name = name

    @staticmethod
    def path ():
        return ('items',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if result['type'] != 'Consumable':
            return None
        if result['details']['type'] != 'Utility':
            return None

        return UtilityConsumable(result['id'], result['name'])


BUILTIN_TYPES = [
    o for o in vars().values()
    if inspect.isclass(o) and issubclass(o, Entity) and o is not Entity]
