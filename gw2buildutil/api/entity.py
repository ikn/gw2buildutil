import abc
import inspect
import re

from .. import build, util


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


_skill_name_mappings = {
    'Mirage Mirror': 'Jaunt',
}

class Skill (Entity):
    def __init__ (self, api_id, name, build_id, storage_build_id, is_chained):
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
        self.build_id = build_id
        self.is_chained = is_chained

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
        name = result['name']
        name = _skill_name_mappings.get(name, name)
        build_id = None
        storage_build_id = None

        prof_api_ids = result.get('professions', ())
        if len(prof_api_ids) == 1:
            if crawler is not None:
                crawler.crawl(Profession, (prof_api_ids[0],))
            prof = storage.from_api_id(Profession, prof_api_ids[0])
            build_id = prof.skills_build_ids.get(api_id)
            if build_id is not None:
                storage_build_id = Skill._storage_build_id(prof, build_id)

        return Skill(api_id, name, build_id, storage_build_id,
                     is_chained='prev_chain' in result)

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
        if crawler is not None:
            crawler.crawl(Skill, (result['swap'],))
        swap_skill = storage.from_api_id(Skill, result['swap'])
        name = swap_skill.name
        if name.startswith('Legendary '):
            name = name[len('Legendary '):]
        if name.endswith(' Stance'):
            name = name[:-len(' Stance')]

        def lookup_skill (api_id):
            if crawler is not None:
                crawler.crawl(Skill, (api_id,))
            return storage.from_api_id(Skill, api_id)

        skills = {
            'heal': lookup_skill(result['heal']),
            'utilities': [lookup_skill(api_id)
                          for api_id in result['utilities']],
            'elite': lookup_skill(result['elite']),
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
