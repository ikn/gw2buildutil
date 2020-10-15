import abc
import inspect
import re

from .. import build, util


def _load_dep (entity_type, api_id, storage, crawler):
    if crawler is not None:
        crawler.crawl(entity_type, (api_id,))
    return storage.from_api_id(entity_type, api_id)


class Entity (abc.ABC, util.Identified):
    def __init__ (self, api_id, ids):
        util.Identified.__init__ (self, ids)
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

    @staticmethod
    def _filter_use_first (entities):
        # filter to entity with earliest API ID (for determinism), for each
        # unique name
        by_name = {}
        for e in entities:
            by_name.setdefault(e.name, []).append(e)
        return [sorted(group, key=lambda e: e.api_id)[0]
                for group in by_name.values()]

    @staticmethod
    def filters ():
        return [Entity._filter_use_first]


class Profession (Entity):
    def __init__ (self, api_id, name, build_id, skills_build_ids, weapons):
        Entity.__init__(self, api_id, (name, build_id))
        self.name = name
        self.build_id = build_id
        self.skills_build_ids = skills_build_ids
        self._weapons = weapons

    @staticmethod
    def path ():
        return ('professions',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        skills_build_ids = {
            api_id: build_id
            for build_id, api_id in result.get('skills_by_palette', [])}

        weapons = {}
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
            weapons[weapon_type] = {
                'elite spec api id': weapon_elite_spec_api_id,
                'hands': hands,
            }
        return Profession(
            result['id'], result['name'], result['code'], skills_build_ids,
            weapons)

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
        prof = _load_dep(Profession, result['profession'], storage, crawler)
        return Specialisation(
            result['id'], result['name'], prof, result['elite'])


class Skill (Entity):
    def __init__ (self, api_id, name, type_, professions, weapon_type,
                  build_id, storage_build_id, is_chained, is_aquatic):
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
        if ' ' in id_:
            abbr = ''.join(word[0] for word in id_.split(' ') if word)
            ids.append(abbr)
            if full_id.endswith('!'):
                ids.append(abbr + '!')

        Entity.__init__(self, api_id, ids)
        self.name = name
        self.type_ = type_
        self.professions = professions
        self.weapon_type = weapon_type
        self.build_id = build_id
        self.is_chained = is_chained
        self.is_aquatic = is_aquatic

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
        api_id = result['id']

        if 'type' not in result:
            return None
        try:
            type_ = build.SkillTypes.from_id(result['type'])
        except KeyError:
            return None

        prof_api_ids = result.get('professions', ())
        profs = []
        for prof_api_id in prof_api_ids:
            profs.append(_load_dep(Profession, prof_api_id, storage, crawler))

        if type_ == build.SkillTypes.WEAPON:
            try:
                weapon_type = build.WeaponTypes.from_id(result['weapon_type'])
            except KeyError:
                # probably a downed skill
                type_ = None
                weapon_type = None
        else:
            weapon_type = None

        build_id = None
        storage_build_id = None
        if len(profs) == 1:
            build_id = profs[0].skills_build_ids.get(api_id)
            if build_id is not None:
                storage_build_id = Skill._storage_build_id(profs[0], build_id)

        flags = result.get('flags', ())

        return Skill(api_id, result['name'], type_, profs, weapon_type,
                     build_id, storage_build_id,
                     is_chained='prev_chain' in result,
                     is_aquatic='NoUnderwater' not in flags)

    @staticmethod
    def from_build_id (profession, build_id, storage):
        storage_build_id = Skill._storage_build_id(profession, build_id)
        return storage.from_id(Skill, storage_build_id)

    @staticmethod
    def _filter_not_chained (skills):
        return [s for s in skills if not s.is_chained]

    @staticmethod
    def _filter_has_build_id (skills):
        return [s for s in skills if s.build_id is not None]

    @staticmethod
    def filters ():
        return [
            Skill._filter_not_chained,
            Skill._filter_has_build_id,
        ] + Entity.filters()


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
    def __init__ (self, api_id, name, build_id, skills):
        id_ = name.lower()
        ids = [id_]
        ids.extend(_legend_ids.get(id_, ()))
        ids.append(build_id)

        Entity.__init__(self, api_id, ids)
        self.name = name
        self.build_id = build_id
        self.heal_skill = skills['heal']
        self.utility_skills = tuple(skills['utilities'])
        self.elite_skill = skills['elite']

    @staticmethod
    def crawl_dependencies ():
        return set([Skill])

    @staticmethod
    def path ():
        return ('legends',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        swap_skill = _load_dep(Skill, result['swap'], storage, crawler)
        name = swap_skill.name
        if name.startswith('Legendary '):
            name = name[len('Legendary '):]
        if name.endswith(' Stance'):
            name = name[:-len(' Stance')]

        skills = {
            'heal': _load_dep(Skill, result['heal'], storage, crawler),
            'utilities': [_load_dep(Skill, api_id, storage, crawler)
                          for api_id in result['utilities']],
            'elite': _load_dep(Skill, result['elite'], storage, crawler),
        }

        return RevenantLegend(result['id'], name, result['code'], skills)


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
    def __init__ (self, api_id, name, num_attributes):
        full_id = name
        id_ = full_id.replace('\'s', '')
        ids = [id_]
        if full_id != id_:
            ids.append(full_id)

        Entity.__init__(self, api_id, ids)
        self.name = name
        self.num_attributes = num_attributes

    @staticmethod
    def path ():
        return ('itemstats',)

    @staticmethod
    def from_api (result, storage, crawler=None):
        if not result['name']:
            return None

        return Stats(result['id'], result['name'],
                     num_attributes=len(result['attributes']))

    @staticmethod
    def _filter_endgame (stat_sets):
        return [stats for stats in stat_sets if stats.num_attributes >= 3]

    @staticmethod
    def _filter_not_mixed (stat_sets):
        return [stats for stats in stat_sets if stats.name.find(' and ') < 0]

    @staticmethod
    def filters ():
        return [
            Stats._filter_endgame,
            Stats._filter_not_mixed,
        ] + Entity.filters()


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
        ids = [full_id]
        for prefix in food_prefixes:
            full_prefix = f'{prefix} of '
            if full_id.startswith(full_prefix):
                ids.append(full_id[len(full_prefix):])
                break

        Entity.__init__(self, api_id, ids)
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
