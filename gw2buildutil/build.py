import enum
import abc

from . import util


class BuildError (ValueError):
    pass


def _enum_id_lookup (enum_cls):
    lookup = {}
    for item in enum_cls:
        for id_ in item.value.ids:
            lookup[id_] = item
    return lookup


class GameMode (util.Typed, util.Identified):
    def __init__ (self, name, suitable_game_modes):
        util.Identified.__init__(self, name)
        self.name = name
        self.suitable_game_modes = tuple(suitable_game_modes)


class GameModes (enum.Enum):
    OPEN_WORLD = GameMode('Open World', ('open world', 'dungeons'))
    DUNGEONS = GameMode('Dungeons', ('dungeons',))
    FRACTALS = GameMode('Fractals',
                         ('unorganised fractals', 'dungeons', 'open world'))
    RAIDS = GameMode('Raids', ('casual raids', 'casual organised fractals'))
    PVP = GameMode('PvP', ('PvP',))
    WVW = GameMode('WvW', ('WvW',))

    @staticmethod
    def from_id (id_):
        return _game_modes_id_lookup[util.Identified.normalise_id(id_)]

_game_modes_id_lookup = _enum_id_lookup(GameModes)


class BuildMetadata (util.Typed):
    def __init__ (self, game_mode, profession, elite_spec, labels=()):
        self.game_mode = game_mode # can be None
        self.profession = profession
        self.elite_spec = elite_spec
        self.labels = tuple(labels)

    def __str__ (self):
        return self.title

    def _value (self):
        return (self.game_mode, self.profession, self.elite_spec, self.labels)

    @property
    def title (self):
        spec = self.profession if self.elite_spec is None else self.elite_spec
        prefix = ('' if self.game_mode is None
                  else (self.game_mode.value.name + ' '))
        return f'{prefix}{spec.name}: {", ".join(self.labels)}'


class TextBody:
    def __init__ (self, source):
        self.source = source


class WeaponType (util.Typed, util.Identified):
    def __init__ (self, ids, hands):
        util.Identified.__init__(self, ids)
        self.hands = hands


class WeaponTypes (enum.Enum):
    GREATSWORD = WeaponType(('greatsword', 'gs'), 2)
    HAMMER = WeaponType('hammer', 2)
    LONGBOW = WeaponType(('longbow', 'lb'), 2)
    RIFLE = WeaponType('rifle', 2)
    SHORTBOW = WeaponType(('shortbow', 'sb'), 2)
    STAFF = WeaponType('staff', 2)

    AXE = WeaponType('axe', 1)
    DAGGER = WeaponType('dagger', 1)
    MACE = WeaponType('mace', 1)
    PISTOL = WeaponType('pistol', 1)
    SWORD = WeaponType('sword', 1)
    SCEPTRE = WeaponType(('sceptre', 'scepter'), 1)
    FOCUS = WeaponType('focus', 1)
    SHIELD = WeaponType('shield', 1)
    TORCH = WeaponType('torch', 1)
    WARHORN = WeaponType(('warhorn', 'wh'), 1)

    # disallowed until aquatic weapons are properly supported
    #HARPOON = WeaponType(('harpoon', 'speargun'), 2)
    #SPEAR = WeaponType('spear', 2)
    #TRIDENT = WeaponType('trident', 2)

    @staticmethod
    def from_id (id_):
        return _weapon_types_id_lookup[util.Identified.normalise_id(id_)]

_weapon_types_id_lookup = _enum_id_lookup(WeaponTypes)


class WeaponHand (util.Typed, util.Identified):
    def __init__ (self, ids, hands):
        util.Identified.__init__(self, ids)
        self.hands = hands


class WeaponHands (enum.Enum):
    BOTH = WeaponHand(('both', 'twohand'), 2)
    MAIN = WeaponHand(('main', 'mainhand'), 1)
    OFF = WeaponHand(('off', 'offhand'), 1)

    @staticmethod
    def from_id (id_):
        return _weapon_hands_id_lookup[util.Identified.normalise_id(id_)]

_weapon_hands_id_lookup = _enum_id_lookup(WeaponHands)


class UpgradeTiers (enum.Enum):
    MINOR = 'minor'
    MAJOR = 'major'
    SUPERIOR = 'superior'


class PvpSigil (util.Typed, util.Identified):
    def __init__ (self, name):
        util.Identified.__init__(self, name)
        self.name = name


class PvpSigils (enum.Enum):
    ABSORPTION = PvpSigil('Absorption')
    AGONY = PvpSigil('Agony')
    BATTLE = PvpSigil('Battle')
    CLEANSING = PvpSigil('Cleansing')
    COMPOUNDING = PvpSigil('Compounding')
    CONFUSION = PvpSigil('Confusion')
    COURAGE = PvpSigil('Courage')
    DOOM = PvpSigil('Doom')
    ENERGY = PvpSigil('Energy')
    ENHANCEMENT = PvpSigil('Enhancement')
    ESCAPE = PvpSigil('Escape')
    EXPLOITATION = PvpSigil('Exploitation')
    EXPOSURE = PvpSigil('Exposure')
    INTELLIGENCE = PvpSigil('Intelligence')
    MISERY = PvpSigil('Misery')
    OPPORTUNITY = PvpSigil('Opportunity')
    PERIL = PvpSigil('Peril')
    PURGING = PvpSigil('Purging')
    REVOCATION = PvpSigil('Revocation')
    RUTHLESSNESS = PvpSigil('Ruthlessness')
    SAVAGERY = PvpSigil('Savagery')
    SEPARATION = PvpSigil('Separation')
    SMOLDERING = PvpSigil('Smoldering')
    STAGNATION = PvpSigil('Stagnation')
    VENOM = PvpSigil('Venom')

    @staticmethod
    def from_id (id_):
        return _pvp_sigils_id_lookup[util.Identified.normalise_id(id_)]

_pvp_sigils_id_lookup = _enum_id_lookup(PvpSigils)


class Weapon (util.Typed):
    def __init__ (self, type_, hand, stats, sigils):
        self.type_ = type_
        self.hand = hand
        self.stats = stats
        self.sigils = tuple(sigils)

        if len(self.sigils) != self.hand.value.hands:
            raise BuildError('wrong number of sigils for '
                             '{}: {}'.format(self.hand, len(self.sigils)))

    def __str__ (self):
        return (f'{self.hand.value}-hand {self.stats} {self.type_.value} '
                f'({", ".join(map(str, self.sigils))})')

    def _value (self):
        return (self.type_, self.hand, self.stats, self.sigils)


class Weapons (util.Typed):
    def __init__ (self, set1, set2=None):
        self.set1 = tuple(set1)
        self.set2 = None if set2 is None else tuple(set2)

        for set_ in (self.set1, self.set2):
            if set_ is None:
                continue
            hands = {weapon.hand for weapon in set_}
            if hands not in (
                {WeaponHands.BOTH},
                {WeaponHands.MAIN, WeaponHands.OFF}
            ):
                raise BuildError(
                    'invalid weapon set: '
                    f'{", ".join(weapon.type_.name for weapon in set_)}')

    def _value (self):
        return (self.set1, self.set2)

    def check_profession (self, profession, elite_spec):
        for set_ in (self.set1, self.set2):
            if set_ is None:
                continue
            for weapon in set_:
                if not profession.can_wield(weapon, elite_spec):
                    spec = profession if elite_spec is None else elite_spec
                    raise BuildError(
                        f'{spec.name} cannot wield '
                        f'{weapon.type_.name} in {weapon.hand.name}')


class PvpRune (util.Typed, util.Identified):
    def __init__ (self, name):
        util.Identified.__init__(self, name)
        self.name = name


class PvpRunes (enum.Enum):
    ADVENTURE = PvpRune('Adventure')
    AIR = PvpRune('Air')
    ALTRUISM = PvpRune('Altruism')
    BALTHAZAR = PvpRune('Balthazar')
    DIVINITY = PvpRune('Divinity')
    DWAYNA = PvpRune('Dwayna')
    EARTH = PvpRune('Earth')
    EVASION = PvpRune('Evasion')
    EXUBERANCE = PvpRune('Exuberance')
    FIRE = PvpRune('Fire')
    GRENTH = PvpRune('Grenth')
    HOELBRAK = PvpRune('Hoelbrak')
    ICE = PvpRune('Ice')
    INFILTRATION = PvpRune('Infiltration')
    LEADERSHIP = PvpRune('Leadership')
    LYSSA = PvpRune('Lyssa')
    MELANDRU = PvpRune('Melandru')
    ORR = PvpRune('Orr')
    RADIANCE = PvpRune('Radiance')
    RAGE = PvpRune('Rage')
    RATA_SUM = PvpRune('Rata Sum')
    RESISTANCE = PvpRune('Resistance')
    SANCTUARY = PvpRune('Sanctuary')
    SCAVENGING = PvpRune('Scavenging')
    SPEED = PvpRune('Speed')
    STRENGTH = PvpRune('Strength')
    THORNS = PvpRune('Thorns')
    VAMPIRISM = PvpRune('Vampirism')
    AFFLICTED = PvpRune('Afflicted')
    ARISTOCRACY = PvpRune('Aristocracy')
    BAELFIRE = PvpRune('Baelfire')
    BERSERKER = PvpRune('Berserker')
    CENTAUR = PvpRune('Centaur')
    CHRONOMANCER = PvpRune('Chronomancer')
    CITADEL = PvpRune('Citadel')
    DAREDEVIL = PvpRune('Daredevil')
    DEADEYE = PvpRune('Deadeye')
    DOLYAK = PvpRune('Dolyak')
    DRAGONHUNTER = PvpRune('Dragonhunter')
    DRUID = PvpRune('Druid')
    EAGLE = PvpRune('Eagle')
    ELEMENTALIST = PvpRune('Elementalist')
    ENGINEER = PvpRune('Engineer')
    FIGHTER = PvpRune('Fighter')
    FIREBRAND = PvpRune('Firebrand')
    FLAME_LEGION = PvpRune('Flame Legion')
    FLOCK = PvpRune('Flock')
    FORGE = PvpRune('Forge')
    GROVE = PvpRune('Grove')
    GUARDIAN = PvpRune('Guardian')
    HERALD = PvpRune('Herald')
    HOLOSMITH = PvpRune('Holosmith')
    KRAIT = PvpRune('Krait')
    LYNX = PvpRune('Lynx')
    MAD_KING = PvpRune('Mad King')
    MESMER = PvpRune('Mesmer')
    MIRAGE = PvpRune('Mirage')
    MONK = PvpRune('Monk')
    NECROMANCER = PvpRune('Necromancer')
    NIGHTMARE = PvpRune('Nightmare')
    RANGER = PvpRune('Ranger')
    REAPER = PvpRune('Reaper')
    RENEGADE = PvpRune('Renegade')
    REVENANT = PvpRune('Revenant')
    SCHOLAR = PvpRune('Scholar')
    SCRAPPER = PvpRune('Scrapper')
    SOLDIER = PvpRune('Soldier')
    SOULBEAST = PvpRune('Soulbeast')
    SPELLBREAKER = PvpRune('Spellbreaker')
    SUNLESS = PvpRune('Sunless')
    SVANIR = PvpRune('Svanir')
    TEMPEST = PvpRune('Tempest')
    THIEF = PvpRune('Thief')
    TRAPPER = PvpRune('Trapper')
    TRAVELER = PvpRune('Traveler')
    UNDEAD = PvpRune('Undead')
    WARRIOR = PvpRune('Warrior')
    WATER = PvpRune('Water')
    WEAVER = PvpRune('Weaver')
    WURM = PvpRune('Wurm')

    @staticmethod
    def from_id (id_):
        return _pvp_runes_id_lookup[util.Identified.normalise_id(id_)]

_pvp_runes_id_lookup = _enum_id_lookup(PvpRunes)


class ArmourType (util.Typed, util.Identified):
    def __init__ (self, ids):
        util.Identified.__init__(self, ids)


class ArmourTypes (enum.Enum):
    HELM = ArmourType(('helm', 'head'))
    SHOULDERS = ArmourType('shoulders')
    COAT = ArmourType(('coat', 'chest'))
    GLOVES = ArmourType(('gloves', 'hands'))
    LEGGINGS = ArmourType(('leggings', 'legs'))
    BOOTS = ArmourType(('boots', 'feet'))

    @staticmethod
    def from_id (id_):
        return _armour_types_id_lookup[util.Identified.normalise_id(id_)]

_armour_types_id_lookup = _enum_id_lookup(ArmourTypes)


class ArmourPiece (util.Typed):
    def __init__ (self, type_, stats, rune):
        self.type_ = type_
        self.stats = stats
        self.rune = rune

    def __str__ (self):
        return f'{self.stats} {self.type_.value} ({self.rune})'

    def _value (self):
        return (self.type_, self.stats, self.rune)


class Armour (util.Typed):
    def __init__ (self, pieces):
        self.pieces = {p.type_: p for p in pieces}

        if len(pieces) != 6:
            raise BuildError('expected 6 armour pieces, got '
                             '{}'.format(len(pieces)))
        if len(self.pieces) != 6:
            raise BuildError('not all armour types are present: '
                             '{}'.format(list(self.pieces.keys())))

    def _value (self):
        return tuple(self.pieces.items())


class PvpArmour (util.Typed):
    def __init__ (self, rune):
        self.rune = rune

    def __str__ (self):
        return str(self.rune)

    def _value (self):
        return self.rune


class TrinketTypes (enum.Enum):
    BACK = 'back'
    ACCESSORY_1 = 'accessory 1'
    ACCESSORY_2 = 'accessory 2'
    AMULET = 'amulet'
    RING_1 = 'ring 1'
    RING_2 = 'ring 2'


class Trinket (util.Typed):
    def __init__ (self, type_, stats):
        self.type_ = type_
        self.stats = stats

    def __str__ (self):
        return f'{self.stats} {self.type_.value}'

    def _value (self):
        return (self.type_, self.stats)


class Trinkets (util.Typed):
    def __init__ (self, pieces):
        self.pieces = {p.type_: p for p in pieces}

        if len(pieces) != 6:
            raise BuildError('expected 6 trinkets, got '
                             '{}'.format(len(pieces)))
        if len(self.pieces) != 6:
            raise BuildError('not all trinket types are present: '
                             '{}'.format(list(self.pieces.keys())))

    def _value (self):
        return tuple(self.pieces.items())


class GearGroup (util.Identified):
    def __init__ (self, ids):
        util.Identified.__init__(self, ids)


class GearGroups (enum.Enum):
    WEAPONS = GearGroup('weapons')
    ARMOUR = GearGroup(('armour', 'armor'))
    TRINKETS = GearGroup('trinkets')
    ACCESSORIES = GearGroup('accessories')
    RINGS = GearGroup('rings')

    @staticmethod
    def from_id (id_):
        return _gear_groups_id_lookup[util.Identified.normalise_id(id_)]

_gear_groups_id_lookup = _enum_id_lookup(GearGroups)
_gear_groups_id_lookup.update(_weapon_types_id_lookup)
_gear_groups_id_lookup.update(_armour_types_id_lookup)
_gear_groups_id_lookup.update({type_.value: type_ for type_ in TrinketTypes})


class Consumables (util.Typed):
    def __init__ (self, food=None, utility=None):
        self.food = food
        self.utility = utility

    def _value (self):
        return (self.food, self.utility)


class Gear (util.Typed):
    def __init__ (self, weapons, armour, trinkets, consumables):
        self.weapons = weapons
        self.armour = armour
        self.trinkets = trinkets
        self.consumables = consumables

    def _value (self):
        return (self.weapons, self.armour, self.trinkets, self.consumables)

    def check_profession (self, profession, elite_spec):
        self.weapons.check_profession(profession, elite_spec)


class PvpGear (util.Typed):
    def __init__ (self, stats, weapons, armour):
        self.stats = stats
        self.weapons = weapons
        self.armour = armour

    def _value (self):
        return (self.stats, self.weapons, self.armour)

    def check_profession (self, profession, elite_spec):
        self.weapons.check_profession(profession, elite_spec)


class TraitTier (util.Typed):
    def __init__ (self, api_id, name):
        self.api_id = api_id
        self.name = name

    def _value (self):
        return self.api_id


class TraitTiers (enum.Enum):
    WEAPON = TraitTier(0, 'Weapon')
    ADEPT = TraitTier(1, 'Adept')
    MASTER = TraitTier(2, 'Master')
    GRANDMASTER = TraitTier(3, 'Grandmaster')

    @staticmethod
    def from_api_id (api_id):
        return _trait_tiers_api_id_lookup[api_id]

_trait_tiers_api_id_lookup = {tier.value.api_id: tier for tier in TraitTiers}


class TraitType (util.Typed):
    def __init__ (self, api_id):
        self.api_id = api_id
        self.name = api_id

    def _value (self):
        return self.api_id


class TraitTypes (enum.Enum):
    MINOR = TraitType('Minor')
    MAJOR = TraitType('Major')

    @staticmethod
    def from_api_id (api_id):
        return _trait_types_api_id_lookup[api_id]

_trait_types_api_id_lookup = {type_.value.api_id: type_ for type_ in TraitTypes}


class TraitChoice (util.Typed):
    def __init__ (self, index, name):
        self.index = index
        self.api_id = index
        self.name = name

    def _value (self):
        return self.index


class TraitChoices (enum.Enum):
    TOP = TraitChoice(0, 'Top')
    MIDDLE = TraitChoice(1, 'Middle')
    BOTTOM = TraitChoice(2, 'Bottom')

    @staticmethod
    def from_index (index):
        return _trait_choices_index_lookup[index]

    @staticmethod
    def from_api_id (api_id):
        return TraitChoices.from_index(api_id)

_trait_choices_index_lookup = {choice.value.index: choice
                               for choice in TraitChoices}


class SpecialisationChoices (util.Typed):
    def __init__ (self, spec, choices):
        self.spec = spec
        self.choices = tuple(choices) # items can be None

        if len(self.choices) != 3:
            raise BuildError('expected 3 trait choices, got '
                             f'{len(self.choices)}')

    def __str__ (self):
        return (f'{self.spec} '
                f'{" ".join(str(choice.value) for choice in self.choices)}')

    def _value (self):
        return (self.spec, self.choices)


class Traits (util.Typed):
    def __init__ (self, specs):
        self.specs = tuple(specs) # items can be None

        if len(self.specs) != 3:
            raise BuildError('expected 3 specialisations, got '
                             f'{len(self.specs)}')

        spec_api_ids = set()
        for spec_choices in self.specs:
            if spec_choices is None:
                continue
            spec = spec_choices.spec
            if spec_choices.spec.api_id in spec_api_ids:
                raise BuildError('duplicate specialisation: '
                                 f'{spec_choices.spec.name}')
            spec_api_ids.add(spec_choices.spec.api_id)

        elite_specs = [spec_choices.spec for spec_choices in self.specs
                       if spec_choices.spec.is_elite]
        if len(elite_specs) > 1:
            raise BuildError('multiple elite specialisations are selected: '
                             f'{", ".join(spec.name for spec in elite_specs)}')

    def _value (self):
        return self.specs

    def check_profession (self, profession, elite_spec):
        actual_elite_spec = None
        for spec_choices in self.specs:
            if spec_choices is None:
                continue
            if spec_choices.spec.profession != profession:
                raise BuildError(f'not a specialisation for {profession.name}: '
                                 f'{spec_choices.spec.name}')
            if spec_choices.spec.is_elite:
                actual_elite_spec = spec_choices.spec

        if elite_spec is None and actual_elite_spec is not None:
            raise BuildError(
                'no elite specialisation is declared in build metadata, '
                f'but {actual_elite_spec.name} is selected in traits')
        if elite_spec is not None and actual_elite_spec != elite_spec:
            raise BuildError(
                f'elite specialisation {elite_spec.name} is declared in '
                f'build metadata, but not selected in traits')


class SkillType (util.Identified):
    def __init__ (self, ids):
        util.Identified.__init__(self, ids)


class SkillTypes (enum.Enum):
    WEAPON = SkillType('weapon')
    HEAL = SkillType('heal')
    UTILITY = SkillType('utility')
    ELITE = SkillType('elite')
    PROFESSION = SkillType('profession')
    BUNDLE = SkillType('bundle')
    TOOLBELT = SkillType('toolbelt')
    PET = SkillType('pet')

    @staticmethod
    def from_id (id_):
        return _skill_types_id_lookup[util.Identified.normalise_id(id_)]

_skill_types_id_lookup = _enum_id_lookup(SkillTypes)


class Skills (util.Typed):
    def __init__ (self, heal, utilities, elite):
        # skills can be None
        self.heal = heal
        self.utilities = tuple(utilities)
        self.elite = elite

        if self.heal is not None and self.heal.type_ != SkillTypes.HEAL:
            raise BuildError(f'not a heal skill: {self.heal.name}')

        if len(self.utilities) != 3:
            raise BuildError('expected 3 utility skills, got '
                             f'{len(self.utilities)}')
        utility_api_ids = set()
        for utility in self.utilities:
            if utility is not None:
                if utility.type_ != SkillTypes.UTILITY:
                    raise BuildError(f'not a utility skill: {utility.name}')
                if utility.api_id in utility_api_ids:
                    raise BuildError(f'duplicate utility skill: {utility.name}')
                utility_api_ids.add(utility.api_id)
        if self.elite is not None and self.elite.type_ != SkillTypes.ELITE:
            raise BuildError(f'not an elite skill: {self.elite.name}')

    def _value (self):
        return (self.heal, self.utilities, self.elite)

    def check_profession (self, profession, elite_spec):
        for skill in (self.heal,) + self.utilities + (self.elite,):
            if skill is None:
                continue

            if skill.profession is not None and skill.profession != profession:
                raise BuildError(f'not a skill for {profession.name}: '
                                 f'{skill.name}')

            if skill.elite_spec is not None and skill.elite_spec != elite_spec:
                raise BuildError(f'skill requires {skill.elite_spec.name}: '
                                 f'{skill.name}')

    def check_aquatic (self):
        for skill in (self.heal,) + self.utilities + (self.elite,):
            if skill is not None and not skill.is_aquatic:
                raise BuildError(f'skill not usable underwater: {skill.name}')


class RevenantSkills (util.Typed):
    def __init__ (self, legends):
        self.legends = tuple(legends) # items can be None

        if len(self.legends) != 2:
            raise BuildError(f'expected 2 legends, got {len(self.legends)}')

    def _value (self):
        return self.legends

    def check_profession (self, profession, elite_spec):
        if profession.id_ != 'revenant':
            raise BuildError(f'{profession.name} cannot use Revenant legends')

    def check_aquatic (self):
        for legend in self.legends:
            if legend is not None and not legend.heal_skill.is_aquatic:
                raise BuildError(f'legend not usable underwater: {legend.name}')


class RangerPets (util.Typed):
    def __init__ (self, pets):
        self.pets = tuple(pets) # items can be None

        if len(self.pets) < 1 or len(self.pets) > 2:
            raise BuildError(f'expected 1 or 2 pets, got {len(self.pets)}')

    def _value (self):
        return self.pets


class RangerOptions (util.Typed):
    def __init__ (self, pets, aquatic_pets=None):
        self.pets = pets
        self.aquatic_pets = (RangerPets((None, None))
                             if aquatic_pets is None else aquatic_pets)

    def _value (self):
        return (self.pets, self.aquatic_pets)


class Intro:
    def __init__ (self, url, description, gear, traits, skills,
                  profession_options=None, aquatic_skills=None):
        self.url = url # can be None
        self.description = description # can be None
        self.gear = gear # can be None
        self.traits = traits
        self.skills = skills
        self.aquatic_skills = aquatic_skills
        self.profession_options = profession_options

        if self.aquatic_skills is not None:
            self.aquatic_skills.check_aquatic()

    def check_profession (self, profession, elite_spec):
        if self.gear is not None:
            self.gear.check_profession(profession, elite_spec)
        self.traits.check_profession(profession, elite_spec)
        self.skills.check_profession(profession, elite_spec)
        if self.aquatic_skills is not None:
            self.aquatic_skills.check_profession(profession, elite_spec)


class Boon (util.Typed, util.Identified):
    def __init__ (self, name, extra_ids=()):
        ids = (name,) + (
            (extra_ids,) if isinstance(extra_ids, str) else tuple(extra_ids))
        util.Identified.__init__(self, ids)
        self.name = name


class Boons (enum.Enum):
    AEGIS = Boon('Aegis')
    ALACRITY = Boon('Alacrity')
    FURY = Boon('Fury')
    MIGHT = Boon('Might')
    PROTECTION = Boon('Protection')
    QUICKNESS = Boon('Quickness')
    REGENERATION = Boon('Regeneration')
    RESISTANCE = Boon('Resistance')
    RETALIATION = Boon('Retaliation')
    STABILITY = Boon('Stability')
    SWIFTNESS = Boon('Swiftness')
    VIGOUR = Boon('Vigour', ('vigor',))

    @staticmethod
    def from_id (id_):
        return _boons_id_lookup[util.Identified.normalise_id(id_)]

_boons_id_lookup = _enum_id_lookup(Boons)


class BoonTarget (util.Typed, util.Identified):
    def __init__ (self, num, name):
        util.Identified.__init__(self, (str(num), name))
        self.num = num
        self.name = name


class BoonTargets (enum.Enum):
    PARTY = BoonTarget(5, 'party')
    SQUAD = BoonTarget(10, 'squad')

    @staticmethod
    def from_id (id_):
        return _boon_targets_id_lookup[util.Identified.normalise_id(id_)]

_boon_targets_id_lookup = _enum_id_lookup(BoonTargets)


class BoonUptime:
    def __init__ (self, boon, target, uptime_percent):
        self.boon = boon
        self.target = target
        self.uptime_percent = uptime_percent


class BoonUptimeVariant:
    def __init__ (self, boon_uptimes):
        self.boon_uptimes = boon_uptimes


class BoonNotes:
    def __init__ (self, boon_uptime_variants):
        self.boon_uptime_variants = boon_uptime_variants


class Build:
    def __init__ (self, metadata, intro, alternatives=None, usage=None,
                  notes=None, boon_notes=None, encounters=None):
        self.metadata = metadata
        self.intro = intro
        self.alternatives = alternatives
        self.usage = usage
        self.notes = notes
        self.boon_notes = boon_notes
        self.encounters = encounters

        self.intro.check_profession(self.metadata.profession,
                                    self.metadata.elite_spec)
