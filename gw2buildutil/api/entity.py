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
    def from_api (crawler, storage, result):
        # return instance, or None to skip
        pass

    @abc.abstractmethod
    def to_data (self):
        pass

    @staticmethod
    @abc.abstractmethod
    def from_data (storage, data):
        pass


class Skill (Entity):
    def __init__ (self, api_id, name):
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

        aliases = []
        if ' ' in id_:
            abbr = ''.join(word[0] for word in id_.split(' ') if word)
            aliases.append(abbr)
            if full_id.endswith('!'):
                aliases.append(abbr + '!')

        Entity.__init__(self, api_id, ids, aliases)
        self.name = name

    @staticmethod
    def path ():
        return ('skills',)

    @staticmethod
    def from_api (crawler, storage, result):
        # NOTE: other properties:
        # professions[]
        # *type [ Weapon Heal Utility Elite Profession ]
        # *weapon_type [ None Axe ... ]
        # *slot [ Downed_# Pet Profession_# Utility Weapon_# ]
        # *categories[] [ DualWield StealthAttack ]
        # *attunement [ Fire Water Air Earth ]
        # *dual_wield [ Axe ... ] # off-hand
        if not result.get('professions', ()):
            return None
        if 'prev_chain' in result:
            return None

        return Skill(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return Skill(api_id, name)


class Profession (Entity):
    def __init__ (self, api_id, name):
        Entity.__init__(self, api_id, name)
        self.name = name

    @staticmethod
    def path ():
        return ('professions',)

    @staticmethod
    def from_api (crawler, storage, result):
        return Profession(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return Profession(api_id, name)


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
    def from_api (crawler, storage, result):
        prof_api_id = result['profession']
        crawler.crawl(Profession, (prof_api_id,))
        prof = storage.from_api_id(Profession, prof_api_id)
        return Specialisation(
            result['id'], result['name'], prof, result['elite'])

    def to_data (self):
        return (self.api_id, self.name, self.profession.api_id, self.is_elite)

    @staticmethod
    def from_data (storage, data):
        api_id, name, prof_api_id, is_elite = data
        prof = storage.from_api_id(Profession, prof_api_id)
        return Specialisation(api_id, name, prof, is_elite)


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
    def from_api (crawler, storage, result):
        return RangerPet(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return RangerPet(api_id, name)


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
    def from_api (crawler, storage, result):
        if len(result['attributes']) < 3:
            return None
        if not result['name']:
            return None
        if result['name'].find(' and ') >= 0:
            return None

        return Stats(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return Stats(api_id, name)


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
    def from_api (crawler, storage, result):
        return PvpStats(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return PvpStats(api_id, name)


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
    def from_api (crawler, storage, result):
        if result['type'] != 'UpgradeComponent':
            return None
        if result['details']['type'] != 'Sigil':
            return None
        if result['name'] == 'Legendary Sigil':
            return None

        return Sigil(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return Sigil(api_id, name)


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
    def from_api (crawler, storage, result):
        if result['type'] != 'UpgradeComponent':
            return None
        if result['details']['type'] != 'Rune':
            return None
        if result['name'] in ('', 'Legendary Rune'):
            return None

        return Rune(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return Rune(api_id, name)


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
    def from_api (crawler, storage, result):
        if result['type'] != 'Consumable':
            return None
        if result['details']['type'] != 'Food':
            return None

        return Food(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return Food(api_id, name)


class UtilityConsumable (Entity):
    def __init__ (self, api_id, name):
        Entity.__init__(self, api_id, name)
        self.name = name

    @staticmethod
    def path ():
        return ('items',)

    @staticmethod
    def from_api (crawler, storage, result):
        if result['type'] != 'Consumable':
            return None
        if result['details']['type'] != 'Utility':
            return None

        return UtilityConsumable(result['id'], result['name'])

    def to_data (self):
        return (self.api_id, self.name)

    @staticmethod
    def from_data (storage, data):
        api_id, name = data
        return UtilityConsumable(api_id, name)


BUILTIN_TYPES = [
    o for o in vars().values()
    if inspect.isclass(o) and issubclass(o, Entity) and o is not Entity]
