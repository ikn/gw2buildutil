import abc
import inspect
import re

from .. import build, util

from . import storage as gw2storage


def _load_dep (entity_type, api_id, storage, crawler):
    if crawler is not None:
        crawler.crawl(entity_type, (api_id,))
    return storage.from_api_id(entity_type, api_id)


# should be preferred to _load_dep where possible
def _load_dep_raw (entity_type, api_id, storage, crawler):
    if crawler is not None:
        crawler.crawl_raw(entity_type, (api_id,))
    return storage.raw(entity_type.path(), api_id)


class SkipEntityError (ValueError):
    pass


class Entity (abc.ABC, util.Typed, util.Identified):
    # subclass constructors take arguments (result, storage, crawler)
    # raise SkipEntityError to skip
    def __init__ (self, api_id, ids):
        util.Identified.__init__(self, ids)
        self.api_id = api_id

    def _value (self):
        return self.api_id

    # must not contain ':'
    @classmethod
    def type_id (cls):
        return cls.__name__.lower()

    # just a performance hint - should crawl dependencies in constructor
    # should exclude dependencies used only for ID generation
    @staticmethod
    def crawl_dependencies ():
        return set()

    @staticmethod
    @abc.abstractmethod
    def path ():
        pass

    # relations must not be chained, ie. rely on other relations existing
    # id generation may rely on relations
    def extra_entity_relations (self):
        return {}

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
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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


class Trait (Entity):
    def __init__ (self, result, relations, storage, crawler):
        self.name = result['name']
        self.specialisation = _load_dep(
            Specialisation, result['specialization'], storage, crawler)
        self.tier = build.TraitTiers.from_api_id(result['tier'])
        self.type_ = build.TraitTypes.from_api_id(result['slot'])
        self.choice = (None if self.type_ == build.TraitTypes.MINOR
                       else build.TraitChoices.from_api_id(result['order']))

        ids = [self.name]
        if self.choice is not None:
            ids.append(f'{self.specialisation.name} '
                       f'{self.tier.value.api_id}-'
                       f'{self.choice.value.index + 1}')

        Entity.__init__(self, result['id'], ids)

    @staticmethod
    def crawl_dependencies ():
        return set([Specialisation])

    @staticmethod
    def path ():
        return ('traits',)


class Skill (Entity):
    def __init__ (self, result, relations, storage, crawler):
        api_id = result['id']
        self.name = Skill._name_from_result(result)

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
        if len(self.professions) == 1:
            self.profession = next(iter(self.professions))
        else:
            self.profession = None

        elite_spec_api_id = result.get('specialization')
        self.elite_spec = (
            None if elite_spec_api_id is None
            else _load_dep(Specialisation, elite_spec_api_id, storage, crawler))

        ids = [full_id, id_]
        if ' ' in id_:
            abbr = ''.join(word[0] for word in id_.split(' ') if word)
            ids.append(abbr)
            if full_id.endswith('!'):
                ids.append(abbr + '!')
        ids += self._parse_build_id(api_id)
        ids += self._parse_profession_skill(result)
        ids += self._parse_weapon_skill(result, relations, storage, crawler)
        ids += self._parse_legend_skill(relations, storage, crawler)
        ids += self._parse_toolbelt_skill(relations, storage, crawler)

        Entity.__init__(self, api_id, ids)

        self.is_chained = 'prev_chain' in result
        self.is_flipover = bool(relations.get('flipover', []))
        self.is_aquatic = Skill._is_aquatic_from_result(result)

        self._flipover_skill_api_id = result.get('flip_skill')
        self._bundle_skills_api_ids = result.get('bundle_skills', [])
        self._toolbelt_skill_api_id = result.get('toolbelt_skill')

    def _parse_build_id (self, api_id):
        self.build_id = None
        ids = []
        if self.profession is not None:
            self.build_id = self.profession.skills_build_ids.get(api_id)
            if self.build_id is not None:
                storage_build_id = Skill._storage_build_id(
                    self.profession, self.build_id)
                ids = [storage_build_id]
        return ids

    def _parse_profession_skill (self, result):
        self.profession_slot = None
        if 'slot' in result and result['slot'].startswith('Profession_'):
            try:
                self.profession_slot = int(result['slot'][len('Profession_')])
            except TypeError:
                pass

        ids = []
        if self.profession_slot is not None:
            for prefix in ('profession ', 'prof ', 'f'):
                ids.append(f'{prefix}{self.profession_slot}')
        return ids

    def _parse_weapon_skill (self, result, relations, storage, crawler):
        self.weapon_type = None
        if self.type_ == build.SkillTypes.WEAPON:
            try:
                self.weapon_type = (
                    build.WeaponTypes.from_id(result['weapon_type']))
            except KeyError:
                # probably a downed skill
                self.type_ = None

        self.weapon_slot = None
        if 'slot' in result and result['slot'].startswith('Weapon_'):
            try:
                self.weapon_slot = int(result['slot'][len('Weapon_'):])
            except TypeError:
                pass

        weapon_ids = []
        if self.weapon_slot is not None:
            if self.type_ == build.SkillTypes.WEAPON:
                weapon_ids.extend(self.weapon_type.value.ids)
            elif self.type_ == build.SkillTypes.BUNDLE:
                for _, api_id in relations.get('bundle', []):
                    bundle_skill = _load_dep(Skill, api_id, storage, crawler)
                    weapon_ids.extend(bundle_skill.ids)

        base_ids = []
        if 'attunement' in result:
            attunement = result['attunement']
            base_ids.append(f'{attunement} {self.weapon_slot}')
            base_ids.append(f'{attunement[0]}{self.weapon_slot}')
        elif (result['description'].startswith('Ambush.') and
              self.elite_spec is not None and
              self.elite_spec.id_ == 'mirage' and
              self.type_ == build.SkillTypes.WEAPON
        ):
            base_ids.append('ambush')
        elif (result['description'].startswith('Stealth Attack.') and
              self.profession is not None and
              self.profession.id_ == 'thief' and
              self.type_ == build.SkillTypes.WEAPON
        ):
            base_ids.append('stealth')
            base_ids.append('stealth attack')
        elif ('dual_wield' in result and
              result['dual_wield'].lower() not in ('none', 'nothing')
        ):
            off_weapon_type = build.WeaponTypes.from_id(result['dual_wield'])
            for off_weapon_id in off_weapon_type.value.ids:
                base_ids.append(f'{off_weapon_id} 3')
        else:
            base_ids.append(self.weapon_slot)

        ids = []
        for weapon_id in weapon_ids:
            for base_id in base_ids:
                ids.append(f'{weapon_id} {base_id}')
        return ids

    def _parse_legend_skill (self, relations, storage, crawler):
        ids = []

        if ('legend' in relations and
            self.type_ in (build.SkillTypes.HEAL, build.SkillTypes.ELITE)
        ):
            legend_skill = _load_dep(
                RevenantLegend, relations['legend'][0][1], storage, crawler)
            for legend_id in legend_skill.ids:
                for type_id in self.type_.value.ids:
                    ids.append(f'{legend_id} {type_id}')

        return ids

    def _parse_toolbelt_skill (self, relations, storage, crawler):
        ids = []

        if 'toolbelt' in relations:
            main_skill = _load_dep(
                Skill, relations['toolbelt'][0][1], storage, crawler)
            for main_skill_id in main_skill.ids:
                for suffix in ('toolbelt', 'tb'):
                    ids.append(f'{main_skill_id} {suffix}')

        return ids

    @staticmethod
    def _name_from_result (result):
        return result['name']

    @staticmethod
    def _is_aquatic_from_result (result):
        flags = result.get('flags', ())
        return 'NoUnderwater' not in flags

    @staticmethod
    def crawl_dependencies ():
        return set([Profession, Specialisation])

    @staticmethod
    def path ():
        return ('skills',)

    def extra_entity_relations (self):
        entities = {}
        if self._flipover_skill_api_id is not None:
            entities[(Skill, self._flipover_skill_api_id)] = ['flipover']
        for bundle_skill_api_id in self._bundle_skills_api_ids:
            entities[(Skill, bundle_skill_api_id)] = ['bundle']
        if self._toolbelt_skill_api_id is not None:
            entities[(Skill, self._toolbelt_skill_api_id)] = ['toolbelt']
        return entities

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
        def filter_ (skills):
            core = [s for s in skills if s.elite_spec is None]
            if elite_spec is None:
                return core
            matching = [s for s in skills if s.elite_spec == elite_spec]
            return matching if matching else core

        return gw2storage.Filters((filter_,))

    @staticmethod
    def filter_type (type_):
        return gw2storage.Filters((
            lambda skills: [s for s in skills if s.type_ == type_],
        ))

    filter_is_main = gw2storage.Filters((
        lambda skills: [s for s in skills
                        if not s.is_chained and not s.is_flipover],
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
    def __init__ (self, result, relations, storage, crawler):
        self.name = Skill._name_from_result(_load_dep_raw(
            Skill, result['swap'], storage, crawler))
        self.build_id = result['code']

        api_id = result['id']
        id_ = self.name.lower()
        if id_.startswith('legendary '):
            id_ = id_[len('legendary '):]
        if id_.endswith(' stance'):
            id_ = id_[:-len(' Stance')]
        ids = [id_]
        ids.extend(_legend_ids.get(id_, ()))
        ids.append(self.build_id)

        Entity.__init__(self, api_id, ids)

        self._heal_skill_api_id = result['heal']
        self._utility_skill_api_ids = result['utilities']
        self._elite_skill_api_id = result['elite']
        self.is_aquatic = Skill._is_aquatic_from_result(_load_dep_raw(
            Skill, self._heal_skill_api_id, storage, crawler))

    @staticmethod
    def crawl_dependencies ():
        return set([Skill])

    @staticmethod
    def path ():
        return ('legends',)

    def extra_entity_relations (self):
        api_ids = ([self._heal_skill_api_id] +
                   self._utility_skill_api_ids +
                   [self._elite_skill_api_id])
        return {(Skill, api_id): ['legend'] for api_id in api_ids}

    def heal_skill (self, storage):
        return _load_dep(Skill, self._heal_skill_api_id, storage, None)

    def utility_skills (self, storage):
        return [_load_dep(Skill, api_id, storage, None)
                for api_id in self._utility_skill_api_ids]

    def elite_skill (self, storage):
        return _load_dep(Skill, self._elite_skill_api_id, storage, None)


class RangerPet (Entity):
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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
    def __init__ (self, result, relations, storage, crawler):
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
