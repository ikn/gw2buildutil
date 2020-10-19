import abc
import inspect
import re

from .. import build, util

from . import storage as gw2storage


def _load_dep (entity_type, api_id, storage, crawler):
    if crawler is not None:
        crawler.crawl(entity_type, (api_id,))
    return storage.from_api_id(entity_type, api_id)


class SkipEntityError (ValueError):
    pass


class Entity (abc.ABC, util.Typed, util.Identified):
    # subclass constructors take arguments (result, storage, crawler)
    # raise SkipEntityError to skip
    def __init__ (self, api_id, ids):
        util.Identified.__init__ (self, ids)
        self.api_id = api_id

    def _value (self):
        return self.api_id

    @classmethod
    def type_id (cls):
        # must not contain ':'
        return cls.__name__.lower()

    @staticmethod
    def crawl_dependencies ():
        # just a performance hint - should crawl dependencies in constructor
        return set()

    @staticmethod
    @abc.abstractmethod
    def path ():
        pass

    @staticmethod
    def _filter_first_by_name (entities):
        # filter to entity with earliest API ID (for determinism), for each
        # unique name
        by_name = {}
        for e in entities:
            by_name.setdefault(e.name, []).append(e)
        return [sorted(group, key=lambda e: e.api_id)[0]
                for group in by_name.values()]

    default_filters = gw2storage.Filters((
        lambda entities: Entity._filter_first_by_name(entities),
    ))


class Profession (Entity):
    def __init__ (self, result, storage, crawler):
        self.name = result['name']
        self.build_id = result['code']
        Entity.__init__(self, result['id'], (self.name, self.build_id))

        self.skills_build_ids = {
            api_id: build_id
            for build_id, api_id in result.get('skills_by_palette', [])}

        self._weapons = {}
        for type_id, weapon_result in result['weapons'].items():
            try:
                weapon_type = build.WeaponTypes.from_id(type_id)
            except KeyError:
                continue
            weapon_elite_spec_api_id = weapon_result.get('specialization')
            hands = set()
            for flag in weapon_result['flags']:
                try:
                    hands.add(build.WeaponHands.from_id(flag))
                except KeyError:
                    continue
            self._weapons[weapon_type] = {
                'elite spec api id': weapon_elite_spec_api_id,
                'hands': hands,
            }

    @staticmethod
    def path ():
        return ('professions',)


    def can_wield (self, weapon, elite_spec=None):
        wield_info = self._weapons.get(weapon.type_)
        if wield_info is None:
            return False

        if wield_info['elite spec api id'] is not None:
            if elite_spec is None:
                return False
            if wield_info['elite spec api id'] != elite_spec.api_id:
                return False

        if weapon.hand not in wield_info['hands']:
            return False

        return True


class Specialisation (Entity):
    def __init__ (self, result, storage, crawler):
        self.name = result['name']
        Entity.__init__(self, result['id'], self.name)
        self.profession = _load_dep(
            Profession, result['profession'], storage, crawler)
        self.is_elite = result['elite']

    @staticmethod
    def crawl_dependencies ():
        return set([Profession])

    @staticmethod
    def path ():
        return ('specializations',)


class Skill (Entity):
    def __init__ (self, result, storage, crawler):
        api_id = result['id']
        self.name = result['name']

        full_id = self.name.lower().strip('"')
        id_ = full_id
        if id_.endswith('!'):
            id_ = id_[:-1]
        if ':' in id_:
            id_ = id_[id_.index(':') + 1:].strip()
        if '.' in id_:
            id_ = id_.replace('.', '') # eg. 'A.E.D.'
        if id_.startswith('summon '):
            id_ = id_[len('summon '):]

        if 'type' not in result:
            raise SkipEntityError()
        try:
            self.type_ = build.SkillTypes.from_id(result['type'])
        except KeyError:
            raise SkipEntityError()

        prof_api_ids = result.get('professions', ())
        self.professions = set()
        for prof_api_id in prof_api_ids:
            self.professions.add(
                _load_dep(Profession, prof_api_id, storage, crawler))

        elite_spec_api_id = result.get('specialization')
        self.elite_spec = (
            None if elite_spec_api_id is None
            else _load_dep(Specialisation, elite_spec_api_id, storage, crawler))

        if self.type_ == build.SkillTypes.WEAPON:
            try:
                self.weapon_type = (
                    build.WeaponTypes.from_id(result['weapon_type']))
            except KeyError:
                # probably a downed skill
                self.type_ = None
                self.weapon_type = None
        else:
            self.weapon_type = None

        self.build_id = None
        storage_build_id = None
        if len(self.professions) == 1:
            prof = next(iter(self.professions))
            self.build_id = prof.skills_build_ids.get(api_id)
            if self.build_id is not None:
                storage_build_id = Skill._storage_build_id(prof, self.build_id)

        ids = [id_]
        if full_id != id_:
            ids.append(full_id)
        if storage_build_id is not None:
            ids.append(storage_build_id)
        if ' ' in id_:
            abbr = ''.join(word[0] for word in id_.split(' ') if word)
            ids.append(abbr)
            if full_id.endswith('!'):
                ids.append(abbr + '!')

        Entity.__init__(self, api_id, ids)

        self.is_chained = 'prev_chain' in result

        flags = result.get('flags', ())
        self.is_aquatic = 'NoUnderwater' not in flags

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
    def from_build_id (profession, build_id, storage):
        storage_build_id = Skill._storage_build_id(profession, build_id)
        return storage.from_id(Skill, storage_build_id)

    filter_has_build_id = gw2storage.Filters((
        lambda skills: [s for s in skills if s.build_id is not None],
    ))

    @staticmethod
    def filter_profession (profession):
        return gw2storage.Filters((
            lambda skills: [s for s in skills if profession in s.professions],
        ))

    @staticmethod
    def filter_elite_spec (elite_spec):
        return gw2storage.Filters((
            lambda skills: [s for s in skills if (
                s.elite_spec is None or s.elite_spec == elite_spec
            )],
        ))

    @staticmethod
    def filter_type (type_):
        return gw2storage.Filters((
            lambda skills: [s for s in skills if s.type_ == type_],
        ))


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
    def __init__ (self, result, storage, crawler):
        swap_skill = _load_dep(Skill, result['swap'], storage, crawler)
        self.name = swap_skill.name
        if self.name.startswith('Legendary '):
            self.name = self.name[len('Legendary '):]
        if self.name.endswith(' Stance'):
            self.name = self.name[:-len(' Stance')]

        self.build_id = result['code']

        id_ = self.name.lower()
        ids = [id_]
        ids.extend(_legend_ids.get(id_, ()))
        ids.append(self.build_id)

        api_id = result['id']
        Entity.__init__(self, api_id, ids)

        self.heal_skill = _load_dep(Skill, result['heal'], storage, crawler)
        self.utility_skills = tuple(_load_dep(Skill, api_id, storage, crawler)
                                    for api_id in result['utilities'])
        self.elite_skill = _load_dep(Skill, result['elite'], storage, crawler)

    @staticmethod
    def crawl_dependencies ():
        return set([Skill])

    @staticmethod
    def path ():
        return ('legends',)


class RangerPet (Entity):
    def __init__ (self, result, storage, crawler):
        self.name = result['name']

        full_id = self.name.lower()
        id_ = full_id
        if id_.startswith('juvenile '):
            id_ = id_[len('juvenile '):]
        ids = [id_]
        if full_id != id_:
            ids.append(full_id)

        Entity.__init__(self, result['id'], ids)

    @staticmethod
    def path ():
        return ('pets',)


class Stats (Entity):
    def __init__ (self, result, storage, crawler):
        self.name = result['name']

        full_id = self.name
        id_ = full_id.replace('\'s', '')
        ids = [id_]
        if full_id != id_:
            ids.append(full_id)

        Entity.__init__(self, result['id'], ids)

        self.num_attributes = len(result['attributes'])

    @staticmethod
    def path ():
        return ('itemstats',)

    filter_endgame = gw2storage.Filters((
        lambda stat_sets: [stats for stats in stat_sets
                           if stats.num_attributes >= 3],
        ))

    filter_not_mixed = gw2storage.Filters((
        lambda stat_sets: [stats for stats in stat_sets
                           if stats.name.find(' and ') < 0],
    ))


class PvpStats (Entity):
    def __init__ (self, result, storage, crawler):
        self.name = result['name']

        id_ = self.name.lower()
        if id_.endswith(' amulet'):
            id_ = id_[:-len(' amulet')]

        Entity.__init__(self, result['id'], id_)

    @staticmethod
    def path ():
        return ('pvp', 'amulets')


sigil_pattern = re.compile(r'^'
    r'(?P<tier>\w+) Sigil of (the )?(?P<name>[\w\' ]+)'
    r'$')

class Sigil (Entity):
    def __init__ (self, result, storage, crawler):
        if result['type'] != 'UpgradeComponent':
            raise SkipEntityError()
        if result['details']['type'] != 'Sigil':
            raise SkipEntityError()
        if result['name'] == 'Legendary Sigil':
            raise SkipEntityError()

        self.name = result['name']
        match = sigil_pattern.match(self.name)
        if match is None:
            raise SkipEntityError()
        fields = match.groupdict()
        self.tier = build.UpgradeTiers(fields['tier'].lower())
        ids = [f'{self.tier.value} {fields["name"]}']
        if self.tier == build.UpgradeTiers.SUPERIOR:
            ids.append(fields['name'])

        Entity.__init__(self, result['id'], ids)

    @staticmethod
    def path ():
        return ('items',)


rune_pattern = re.compile(r'^'
    r'(?P<tier>\w+) Rune of (the )?(?P<name>[\w\' ]+)'
    r'$')

class Rune (Entity):
    def __init__ (self, result, storage, crawler):
        if result['type'] != 'UpgradeComponent':
            raise SkipEntityError()
        if result['details']['type'] != 'Rune':
            raise SkipEntityError()
        if result['name'] in ('', 'Legendary Rune'):
            raise SkipEntityError()

        self.name = result['name']
        match = rune_pattern.match(self.name)
        if match is None:
            raise SkipEntityError()
        fields = match.groupdict()
        self.tier = build.UpgradeTiers(fields['tier'].lower())
        ids = [f'{self.tier.value} {fields["name"]}']
        if self.tier == build.UpgradeTiers.SUPERIOR:
            ids.append(fields['name'])

        Entity.__init__(self, result['id'], ids)

    @staticmethod
    def path ():
        return ('items',)


food_prefixes = (
    'plate', 'bowl', 'can', 'pot', 'cup', 'jug', 'bit', 'slice', 'loaf',
    'strip', 'glass', 'handful', 'piece',
)

class Food (Entity):
    def __init__ (self, result, storage, crawler):
        if result['type'] != 'Consumable':
            raise SkipEntityError()
        if result['details']['type'] != 'Food':
            raise SkipEntityError()

        self.name = result['name']

        full_id = self.name.lower()
        ids = [full_id]
        for prefix in food_prefixes:
            full_prefix = f'{prefix} of '
            if full_id.startswith(full_prefix):
                ids.append(full_id[len(full_prefix):])
                break

        Entity.__init__(self, result['id'], ids)

    @staticmethod
    def path ():
        return ('items',)


class UtilityConsumable (Entity):
    def __init__ (self, result, storage, crawler):
        if result['type'] != 'Consumable':
            raise SkipEntityError()
        if result['details']['type'] != 'Utility':
            raise SkipEntityError()

        self.name = result['name']
        Entity.__init__(self, result['id'], self.name)

    @staticmethod
    def path ():
        return ('items',)


BUILTIN_TYPES = [
    o for o in vars().values()
    if inspect.isclass(o) and issubclass(o, Entity) and o is not Entity]
