import enum

from . import util


def _enum_id_lookup (enum_cls):
    lookup = {}
    for item in enum_cls:
        for id_ in item.value.ids:
            lookup[id_] = item
    return lookup


class GameMode (util.Identified):
    def __init__ (self, name, suitable_game_modes):
        util.Identified.__init__(self, name)
        self.name = name
        self.suitable_game_modes = tuple(suitable_game_modes)

    def __str__ (self):
        return self.name


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
        return _game_modes_id_lookup[id_.lower()]

_game_modes_id_lookup = _enum_id_lookup(GameModes)


class BuildMetadata:
    def __init__ (self, game_mode, profession, elite_spec, labels):
        self.game_mode = game_mode
        self.profession = profession
        self.elite_spec = elite_spec
        self.labels = tuple(labels)

    @property
    def title (self):
        spec = self.profession if self.elite_spec is None else self.elite_spec
        return (f'{self.game_mode.value.name} {spec.name}: '
                f'{", ".join(self.labels)}')


class TextBody:
    pass


class MarkdownBody (TextBody):
    def __init__ (self, text):
        self.text = text


class WeaponType (util.Identified):
    def __init__ (self, ids, hands):
        util.Identified.__init__(self, ids)
        self.hands = hands


class WeaponTypes (enum.Enum):
    GREATSWORD = WeaponType('greatsword', 2)
    HAMMER = WeaponType('hammer', 2)
    LONGBOW = WeaponType('longbow', 2)
    RIFLE = WeaponType('rifle', 2)
    SHORTBOW = WeaponType('shortbow', 2)
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
    WARHORN = WeaponType('warhorn', 1)

    HARPOON = WeaponType(('harpoon', 'speargun'), 2)
    SPEAR = WeaponType('spear', 2)
    TRIDENT = WeaponType('trident', 2)

    @staticmethod
    def from_id (id_):
        return _weapon_types_id_lookup[id_.lower()]

_weapon_types_id_lookup = _enum_id_lookup(WeaponTypes)


class WeaponHand (util.Identified):
    def __init__ (self, ids, hands):
        util.Identified.__init__(self, ids)
        self.hands = hands


class WeaponHands (enum.Enum):
    BOTH = WeaponHand('both', 2)
    MAIN = WeaponHand('main', 1)
    OFF = WeaponHand('off', 1)

    @staticmethod
    def from_id (id_):
        return _weapon_hands_id_lookup[id_.lower()]

_weapon_hands_id_lookup = _enum_id_lookup(WeaponHands)


class UpgradeTiers (enum.Enum):
    MINOR = 'minor'
    MAJOR = 'major'
    SUPERIOR = 'superior'


class Sigil:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier


class PvpSigil (util.Identified):
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
        return _pvp_sigils_id_lookup[id_.lower()]

_pvp_sigils_id_lookup = _enum_id_lookup(PvpSigils)


class Weapon:
    def __init__ (self, type_, hand, stats, sigils):
        self.type_ = type_
        self.hand = hand
        self.stats = stats
        self.sigils = tuple(sigils)

        if len(self.sigils) != self.hand.value.hands:
            raise ValueError('wrong number of sigils for '
                             '{}: {}'.format(self.hand, len(self.sigils)))


class Weapons:
    def __init__ (self, set1, set2=None):
        self.set1 = tuple(set1)
        self.set2 = None if set2 is None else tuple(set2)

        if sum(w.hand.value.hands for w in self.set1) != 2:
            raise ValueError('wrong number of weapons in set 1: '
                            '{}'.format(self.set1))
        if (self.set2 is not None and
            sum(w.hand.value.hands for w in self.set2) != 2
        ):
            raise ValueError('wrong number of weapons in set 2: '
                            '{}'.format(self.set1))


class Rune:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier


class PvpRune (util.Identified):
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
        return _pvp_runes_id_lookup[id_.lower()]

_pvp_runes_id_lookup = _enum_id_lookup(PvpRunes)


class ArmourType (util.Identified):
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
        return _armour_types_id_lookup[id_.lower()]

_armour_types_id_lookup = _enum_id_lookup(ArmourTypes)


class ArmourPiece:
    def __init__ (self, type_, stats, rune):
        self.type_ = type_
        self.stats = stats
        self.rune = rune


class Armour:
    def __init__ (self, pieces):
        self.pieces = {p.type_: p for p in pieces}

        if len(pieces) != 6:
            raise ValueError('expected 6 armour pieces, got '
                             '{}'.format(len(pieces)))
        if len(self.pieces) != 6:
            raise ValueError('not all armour types are present: '
                             '{}'.format(list(self.pieces.keys())))


class PvpArmour:
    def __init__ (self, rune):
        self.rune = rune


class TrinketTypes (enum.Enum):
    BACK = 'back'
    ACCESSORY_1 = 'accessory 1'
    ACCESSORY_2 = 'accessory 2'
    AMULET = 'amulet'
    RING_1 = 'ring 1'
    RING_2 = 'ring 2'


class Trinket:
    def __init__ (self, type_, stats):
        self.type_ = type_
        self.stats = stats


class Trinkets:
    def __init__ (self, pieces):
        self.pieces = {p.type_: p for p in pieces}

        if len(pieces) != 6:
            raise ValueError('expected 6 trinkets, got '
                             '{}'.format(len(pieces)))
        if len(self.pieces) != 6:
            raise ValueError('not all trinket types are present: '
                             '{}'.format(list(self.pieces.keys())))


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
        return _gear_groups_id_lookup[id_.lower()]

_gear_groups_id_lookup = _enum_id_lookup(GearGroups)
_gear_groups_id_lookup.update(_weapon_types_id_lookup)
_gear_groups_id_lookup.update(_armour_types_id_lookup)
_gear_groups_id_lookup.update({type_.value: type_ for type_ in TrinketTypes})


class Consumables:
    def __init__ (self, food=None, utility=None):
        self.food = food
        self.utility = utility


class Gear:
    def __init__ (self, weapons, armour, trinkets, consumables):
        self.weapons = weapons
        self.armour = armour
        self.trinkets = trinkets
        self.consumables = consumables


class PvpGear:
    def __init__ (self, stats, weapons, armour):
        self.stats = stats
        self.weapons = weapons
        self.armour = armour


class Specialisation:
    def __init__ (self, name):
        self.name = name


class TraitChoice:
    def __init__ (self, index, name):
        self.index = index
        self.name = name


class TraitChoices (enum.Enum):
    TOP = TraitChoice(0, 'Top')
    MIDDLE = TraitChoice(1, 'Middle')
    BOTTOM = TraitChoice(2, 'Bottom')

    @staticmethod
    def from_index (index):
        return _trait_choices_index_lookup[index]

_trait_choices_index_lookup = {choice.value.index: choice
                               for choice in TraitChoices}


class SpecialisationChoices:
    def __init__ (self, spec, choices):
        self.spec = spec
        self.choices = tuple(choices)

        if len(self.choices) != 3:
            raise ValueError('expected 3 trait choices, got '
                             f'{len(self.choices)}')


class Traits:
    def __init__ (self, specs):
        self.specs = tuple(specs)

        if len(self.specs) != 3:
            raise ValueError('expected 3 specialisations, got '
                             f'{len(self.specs)}')


class Skills:
    def __init__ (self, heal, utilities, elite):
        self.heal = heal
        self.utilities = tuple(utilities)
        self.elite = elite

        if len(self.utilities) != 3:
            raise ValueError('expected 3 utility skills, got '
                             f'{len(self.utilities)}')


class RevenantLegend (util.Identified):
    def __init__ (self, name, extra_ids=()):
        ids = (name,) + (
            (extra_ids,) if isinstance(extra_ids, str) else tuple(extra_ids))
        util.Identified.__init__(self, ids)
        self.name = name


class RevenantLegends (enum.Enum):
    ASSASSIN = RevenantLegend('Assassin', ('shiro',))
    CENTAUR = RevenantLegend('Centaur', ('ventari',))
    DEMON = RevenantLegend('Demon', ('mallyx',))
    DWARF = RevenantLegend('Dwarf', ('jalis',))

    DRAGON = RevenantLegend('Dragon', ('glint', 'herald'))
    RENEGADE = RevenantLegend('Renegade', ('kalla',))

    @staticmethod
    def from_id (id_):
        return _revenant_legends_id_lookup[id_.lower()]

_revenant_legends_id_lookup = _enum_id_lookup(RevenantLegends)


class RevenantSkills:
    def __init__ (self, legends):
        self.legends = tuple(legends)

        if len(self.legends) != 2:
            raise ValueError(f'expected 2 legends, got {len(self.legends)}')


class RangerPets:
    def __init__ (self, pets):
        self.pets = tuple(pets)

        if len(self.pets) < 1 or len(self.pets) > 2:
            raise ValueError(f'expected 1 or 2 pets, got {len(self.pets)}')


class Intro:
    def __init__ (self, url, description, gear, traits, skills,
                  profession_options=None):
        self.url = url
        self.description = description
        self.gear = gear
        self.traits = traits
        self.skills = skills
        self.profession_options = profession_options


class Boon (util.Identified):
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
        return _boons_id_lookup[id_.lower()]

_boons_id_lookup = _enum_id_lookup(Boons)


class BoonTarget (util.Identified):
    def __init__ (self, num, name):
        util.Identified.__init__(self, (str(num), name))
        self.num = num
        self.name = name


class BoonTargets (enum.Enum):
    PARTY = BoonTarget(5, 'party')
    SQUAD = BoonTarget(10, 'squad')

    @staticmethod
    def from_id (id_):
        return _boon_targets_id_lookup[id_.lower()]

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
