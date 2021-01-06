import abc
import operator

from . import build as gw2build, util


def _walk_path (record, path):
    for attr in path:
        if isinstance(record, util.Record):
            record = getattr(record, attr)
        else:
            record = record[attr]
    return record


def _modify_record (record, path, value):
    if not path:
        return value
    elif record is None:
        return None
    elif isinstance(record, util.Record):
        return record.modify({
            path[0]: _modify_record(getattr(record, path[0]), path[1:], value)
        })
    elif isinstance(record, dict):
        new_record = dict(record)
        new_record[path[0]] = _modify_record(record[path[0]], path[1:], value)
        return new_record
    else:
        item = _modify_record(record[path[0]], path[1:], value)
        return tuple(record[:path[0]]) + (item,) + tuple(record[path[0] + 1:])


def _modify_simple (build, current_path, new_value,
                    old_value=None, is_new_value=None, is_old_value=None,
                    value_is_seq=False):
    if is_new_value is None:
        is_new_value = lambda value: value == new_value
    if is_old_value is None:
        is_old_value = lambda value: value == old_value

    current_value = _walk_path(build, current_path)
    is_seq = not value_is_seq and isinstance(current_value, tuple)
    if not is_seq:
        current_value = (current_value,)

    target_index = None
    for i, value in enumerate(current_value):
        if is_new_value(value):
            if old_value is not None:
                raise ModificationError(f'expected to replace {old_value}, but '
                                        f'{new_value} is already selected')
            target_index = i
            break

    if target_index is None:
        for i, value in enumerate(current_value):
            if (value is not None and
                old_value is not None and
                is_old_value(value)
            ):
                target_index = i
                break
    if target_index is None and old_value is not None:
        raise ModificationError(f'expected to replace {old_value}, but '
                                'it\'s not selected')

    if target_index is None:
        for i, value in enumerate(current_value):
            if value is None:
                target_index = i
                break

    if target_index is None:
        target_index = len(current_value) - 1

    path = list(current_path)
    if is_seq:
        path.append(target_index)
    return _modify_record(build, path, new_value)


def _check_type (mod, component, expect_type):
    if not isinstance(component, expect_type):
        raise ModificationError(
            f'cannot apply {type(mod).__name__} modification: build has '
            f'{type(build.intro.gear).__name__}, expected '
            f'{expect_type.__name__}')


class ModificationError (Exception):
    pass


class Modification (abc.ABC):
    @abc.abstractmethod
    def modify (self, build):
        pass


class WeaponTypeMod (Modification):
    def __init__ (self, new_weapon_types, old_weapon_types=None):
        self.new_weapon_types = new_weapon_types
        self.old_weapon_types = old_weapon_types

    def _norm_types (self, types, old_types, build, arg_name):
        if isinstance(types, gw2build.WeaponTypes):
            prof = build.metadata.profession
            spec = (prof if build.metadata.elite_spec is None
                    else build.metadata.elite_spec)
            hands = prof.can_wield_type(types, build.metadata.elite_spec)
            both = gw2build.WeaponHands.BOTH in hands
            main = gw2build.WeaponHands.MAIN in hands
            off = gw2build.WeaponHands.OFF in hands

            if both:
                return (types,)
            elif main and off:
                if old_types is not None and len(old_types) == 2:
                    if old_types[0] is not None and old_types[1] is None:
                        return (types, None)
                    elif old_types[0] is None and old_types[1] is not None:
                        return (None, types)
                raise ModificationError(
                    f'{spec} can wield {types} in either hand: '
                    f'{arg_name} should be a sequence')
            elif not main and not off:
                raise ModificationError(f'{spec} cannot wield {types}')
            elif main:
                return (types, None)
            else:
                return (None, types)

        else:
            return types

    def _sets_to_replace (self, old_types, build):
        current_weapons = build.intro.gear.weapons

        if old_types is None:
            current_set_attr = (
                'set1' if current_weapons.set2 is None else 'set2')
            current_set = getattr(current_weapons, current_set_attr)
            other_set = (None if current_weapons.set2 is None
                        else current_weapons.set1)
            yield (current_set_attr, current_set, other_set)

        else:
            target_found = False
            for current_set_attr, other_set_attr in (
                ('set1', 'set2'), ('set2', 'set1')
            ):
                current_set = getattr(current_weapons, current_set_attr)
                if (current_set is not None and
                    len(current_set) == len(old_types) and
                    all(old_type is None or old_type == w.type_
                        for w, old_type in zip(current_set, old_types))
                ):
                    target_found = True
                    yield (current_set_attr, current_set,
                           getattr(current_weapons, other_set_attr))

            if not target_found:
                raise ModificationError(f'expected to replace {old_types}, but '
                                        'no weapon set matches')

    def _merge_types (self, new_types, current_set, other_set):
        if len(new_types) == len(current_set):
            base_set = current_set
        elif other_set is not None and len(new_types) == len(other_set):
            base_set = other_set
        else:
            base_set = None
        if base_set is None:
            merged_types = new_types
        else:
            merged_types = [base.type_ if new is None else new
                            for new, base in zip(new_types, base_set)]
        if None in merged_types:
            raise ModificationError(
                f'missing weapon after applying modification: {merged_types}')
        return merged_types

    def _merge_details (self, new_types, base_set):
        base_weapons = {w.hand: w for w in base_set}
        B = gw2build.WeaponHands.BOTH
        M = gw2build.WeaponHands.MAIN
        O = gw2build.WeaponHands.OFF
        if B in base_weapons:
            stats = [base_weapons[B].stats, base_weapons[B].stats]
            sigils = base_weapons[B].sigils
        else:
            stats = [base_weapons[M].stats, base_weapons[O].stats]
            sigils = base_weapons[M].sigils + base_weapons[O].sigils

        if len(new_types) == 2:
            return [gw2build.Weapon(new_types[0], M, stats[0], [sigils[0]]),
                    gw2build.Weapon(new_types[1], O, stats[1], [sigils[1]])]
        elif stats[0] == stats[1]:
            return [gw2build.Weapon(new_types[0], B, stats[0], sigils)]
        else:
            raise ModificationError(
                'cannot replace 2 1-handed weapons with different stats with a '
                f'2-handed weapon ({base_set} -> {new_types[0]})')

    def modify (self, build):
        if self.old_weapon_types is None:
            old_types = None
        else:
            old_types = self._norm_types(
                self.old_weapon_types, None, build, 'old_weapon_types')
        new_types = self._norm_types(
            self.new_weapon_types, old_types, build, 'new_weapon_types')

        for current_set_attr, current_set, other_set in \
            self._sets_to_replace(old_types, build) \
        :
            merged_types = self._merge_types(new_types, current_set, other_set)
            merged_set = self._merge_details(merged_types, current_set)

            build = _modify_simple(
                build, ('intro', 'gear', 'weapons', current_set_attr),
                merged_set, value_is_seq=True)

        return build


class SigilMod (Modification):
    def __init__ (self, new_sigil, old_sigil=None):
        self.new_sigil = new_sigil
        self.old_sigil = old_sigil

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)

        base_path = ('intro', 'gear', 'weapons')
        succeeded = False
        mod_error = None
        for set_attr in ('set1', 'set2'):
            current_weapon_set = getattr(build.intro.gear.weapons, set_attr)
            if current_weapon_set is None:
                continue

            # operate on whole set of sigils as a single sequence
            current_sigils = sum(
                (weapon.sigils for weapon in current_weapon_set), ())
            try:
                new_sigils = _modify_simple(current_sigils, (),
                                            self.new_sigil, self.old_sigil)
            except ModificationError as e:
                # sigil we want to replace might only be on 1 weapon set
                mod_error = e
                continue
            else:
                succeeded = True

            # pull the updated sigils back out into the configured weapons
            new_weapon_set = []
            used_sigils = 0
            for weapon in current_weapon_set:
                num_sigils = len(weapon.sigils)
                new_weapon_set.append(weapon.modify({
                    'sigils': new_sigils[used_sigils:used_sigils + num_sigils],
                }))
                used_sigils += num_sigils

            build = _modify_simple(build, base_path + (set_attr,),
                                   new_weapon_set, value_is_seq=True)

        if not succeeded:
            raise mod_error

        return build


class WeaponStatsMod (Modification):
    def __init__ (self, stats, weapon_types=gw2build.WeaponTypes,
                  weapon_hands = gw2build.WeaponHands):
        self.stats = stats
        self.weapon_types = set(weapon_types)
        self.weapon_hands = set(weapon_hands)

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)

        base_path = ('intro', 'gear', 'weapons')
        for set_attr in ('set1', 'set2'):
            weapon_set = getattr(build.intro.gear.weapons, set_attr)
            if weapon_set is None:
                continue

            for index, weapon in enumerate(weapon_set):
                if (weapon.type_ not in self.weapon_types or
                    weapon.hand not in self.weapon_hands
                ):
                    continue

                build = _modify_simple(
                    build, base_path + (set_attr, index, 'stats'),
                    self.stats)

        return build


class ArmourStatsMod (Modification):
    def __init__ (self, stats, armour_types=gw2build.ArmourTypes):
        self.stats = stats
        self.armour_types = tuple(armour_types)

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)

        for type_ in self.armour_types:
            build = _modify_simple(
                build, ('intro', 'gear', 'armour', 'pieces', type_, 'stats'),
                self.stats)

        return build


class RuneMod (Modification):
    def __init__ (self, rune):
        self.rune = rune

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)

        for type_ in gw2build.ArmourTypes:
            build = _modify_simple(
                build, ('intro', 'gear', 'armour', 'pieces', type_, 'rune'),
                self.rune)

        return build


class PvpRuneMod (Modification):
    def __init__ (self, rune):
        self.rune = rune

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.PvpGear)
        return _modify_simple(
            build, ('intro', 'gear', 'armour', 'rune'), self.rune)


class TrinketStatsMod (Modification):
    def __init__ (self, stats, trinket_types=gw2build.TrinketTypes):
        self.stats = stats
        self.trinket_types = tuple(trinket_types)

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)

        for type_ in self.trinket_types:
            build = _modify_simple(
                build, ('intro', 'gear', 'trinkets', 'pieces', type_, 'stats'),
                self.stats)

        return build


class FoodMod (Modification):
    def __init__ (self, food):
        self.food = food

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)
        return _modify_simple(
            build, ('intro', 'gear', 'consumables', 'food'), self.food)


class UtilityConsumableMod (Modification):
    def __init__ (self, utility):
        self.utility = utility

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.Gear)
        return _modify_simple(
            build, ('intro', 'gear', 'consumables', 'utility'), self.utility)


class StatsMod (Modification):
    def __init__ (self, stats):
        self.stats = stats

    def modify (self, build):
        for mod in (
            WeaponStatsMod(self.stats),
            ArmourStatsMod(self.stats),
            TrinketStatsMod(self.stats),
        ):
            build = mod.modify(build)

        return build


class PvpStatsMod (Modification):
    def __init__ (self, stats):
        self.stats = stats

    def modify (self, build):
        _check_type(self, build.intro.gear, gw2build.PvpGear)
        return _modify_simple(
            build, ('intro', 'gear', 'stats'), self.stats)


class TraitMod (Modification):
    def __init__ (self, new_trait):
        self.new_trait = new_trait

        if self.new_trait.type_ != gw2build.TraitTypes.MAJOR:
            raise ValueError(f'not a major trait: {self.new_trait}')

    def modify (self, build):
        for spec_index, spec_choices in enumerate(build.intro.traits.specs):
            if (spec_choices is not None and
                spec_choices.spec == self.new_trait.specialisation
            ):
                path = ('intro', 'traits', 'specs', spec_index, 'choices',
                        self.new_trait.tier.value.index)
                return _modify_record(build, path, self.new_trait.choice)

        raise ModificationError(
            f'cannot select {self.new_trait} because '
            f'{self.new_trait.specialisation} is not selected')


class SpecChoicesMod (Modification):
    def __init__ (self, new_spec_choices, old_spec=None):
        self.new_spec_choices = new_spec_choices
        self.old_spec = old_spec

    def modify (self, build):
        return _modify_simple(
            build, ('intro', 'traits', 'specs'),
            self.new_spec_choices, self.old_spec,
            is_new_value=lambda spec_choices: (
                spec_choices.spec == self.new_spec_choices.spec),
            is_old_value=lambda spec_choices: (
                spec_choices.spec == self.old_spec))


class SkillMod (Modification):
    _SKILL_TYPES = {
        gw2build.SkillTypes.HEAL: 'heal',
        gw2build.SkillTypes.UTILITY: 'utilities',
        gw2build.SkillTypes.ELITE: 'elite',
    }

    def __init__ (self, new_skill, old_skill=None):
        self.new_skill = new_skill
        self.old_skill = old_skill

        if self.new_skill.type_ not in SkillMod._SKILL_TYPES:
            raise ValueError(f'not a slottable skill: {self.new_skill}')
        if (self.old_skill is not None and
            self.old_skill.type_ not in SkillMod._SKILL_TYPES
        ):
            raise ValueError(f'not a slottable skill: {self.old_skill}')
        if (self.old_skill is not None and
            self.new_skill.type_ != self.old_skill.type_
        ):
            raise ValueError('mismatched skill types: cannot replace '
                             f'{self.old_skill} with {self.new_skill}')

    def modify (self, build):
        _check_type(self, build.intro.skills, gw2build.Skills)
        type_attr = SkillMod._SKILL_TYPES[self.new_skill.type_]
        return _modify_simple(build, ('intro', 'skills', type_attr),
                              self.new_skill, self.old_skill)


class RevenantLegendMod (Modification):
    def __init__ (self, new_legend, old_legend=None):
        self.new_legend = new_legend
        self.old_legend = old_legend

    def modify (self, build):
        _check_type(self, build.intro.skills, gw2build.RevenantSkills)
        return _modify_simple(build, ('intro', 'skills', 'legends'),
                              self.new_legend, self.old_legend)


class RangerPetMod (Modification):
    def __init__ (self, new_pet, old_pet=None):
        self.new_pet = new_pet
        self.old_pet = old_pet

    def modify (self, build):
        _check_type(self, build.intro.profession_options,
                    gw2build.RangerOptions)
        return _modify_simple(
            build, ('intro', 'profession_options', 'pets', 'pets'),
            self.new_pet, self.old_pet)


def modify (build, modifications):
    for mod in modifications:
        build = mod.modify(build)
    return build
