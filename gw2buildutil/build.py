import enum


class _Identified:
    def __init__ (self, ids):
        ids = (ids,) if isinstance(ids, str) else ids
        self.id_ = ids[0]
        self.all_ids = tuple(ids)


def _enum_id_lookup (enum_cls):
    lookup = {}
    for item in enum_cls:
        for id_ in item.value.all_ids:
            lookup[id_] = item
    return lookup


class GameMode (_Identified):
    def __init__ (self, ids, name, suitable_game_modes):
        _Identified.__init__(self, ids)
        self.name = name
        self.suitable_game_modes = tuple(suitable_game_modes)

    def __str__ (self):
        return self.name


class GameModes (enum.Enum):
    OPEN_WORLD = GameMode('open world', 'Open World',
                          ('open world', 'dungeons'))
    DUNGEONS = GameMode('dungeons', 'Dungeons', ('dungeons',))
    FRACTALS = GameMode('fractals', 'Fractals',
                         ('unorganised fractals', 'dungeons', 'open world'))
    RAIDS = GameMode('raids', 'Raids',
                      ('casual raids', 'casual organised fractals'))
    PVP = GameMode('pvp', 'PvP', ('PvP',))
    WVW = GameMode('wvw', 'WvW', ('WvW',))

    @staticmethod
    def from_id (id_):
        return _game_modes_id_lookup[id_]

_game_modes_id_lookup = _enum_id_lookup(GameModes)


class Profession:
    def __init__ (self, profession, elite_spec=None):
        self.profession = profession
        self.elite_spec = elite_spec

    def __str__ (self):
        return self.profession if self.elite_spec is None else self.elite_spec

    def same_base (self, other):
        return self.profession == other.profession


class BuildMetadata:
    def __init__ (self, game_mode, profession, labels):
        self.game_mode = game_mode
        self.profession = profession
        self.labels = tuple(labels)

    @property
    def title (self):
        return '{} {}: {}'.format(self.game_mode, self.profession,
                                  ', '.join(self.labels))


class TextBody:
    pass


class MarkdownBody (TextBody):
    def __init__ (self, text):
        self.text = text


class Stats (_Identified):
    def __init__ (self, ids, name):
        _Identified.__init__(self, ids)
        self.name = name


class StatsEnum (enum.Enum):
    APOTHECARY = Stats('apothecary', 'Apothecary')
    ASSASSIN = Stats('assassin', 'Assassin')
    BERSERKER = Stats('berserker', 'Berserker')
    BRINGER = Stats('bringer', 'Bringer')
    CAPTAIN = Stats('captain', 'Captain')
    CARRION = Stats('carrion', 'Carrion')
    CAVALIER = Stats('cavalier', 'Cavalier')
    CELESTIAL = Stats('celestial', 'Celestial')
    CLERIC = Stats('cleric', 'Cleric')
    COMMANDER = Stats('commander', 'Commander')
    CRUSADER = Stats('crusader', 'Crusader')
    DIRE = Stats('dire', 'Dire')
    DIVINER = Stats('diviner', 'Diviner')
    GIVER = Stats('giver', 'Giver')
    GRIEVING = Stats('grieving', 'Grieving')
    HARRIER = Stats('harrier', 'Harrier')
    KNIGHT = Stats('knight', 'Knight')
    MAGI = Stats('magi', 'Magi')
    MARAUDER = Stats('marauder', 'Marauder')
    MARSHAL = Stats('marshal', 'Marshal')
    MINSTREL = Stats('minstrel', 'Minstrel')
    NOMAD = Stats('nomad', 'Nomad')
    PLAGUEDOCTOR = Stats('plaguedoctor', 'Plaguedoctor')
    RABID = Stats('rabid', 'Rabid')
    RAMPAGER = Stats('rampager', 'Rampager')
    SENTINEL = Stats('sentinel', 'Sentinel')
    SERAPH = Stats('seraph', 'Seraph')
    SETTLER = Stats('settler', 'Settler')
    SHAMAN = Stats('shaman', 'Shaman')
    SINISTER = Stats('sinister', 'Sinister')
    SOLDIER = Stats('soldier', 'Soldier')
    TRAILBLAZER = Stats('trailblazer', 'Trailblazer')
    VALKYRIE = Stats('valkyrie', 'Valkyrie')
    VIGILANT = Stats('vigilant', 'Vigilant')
    VIPER = Stats('viper', 'Viper')
    WANDERER = Stats('wanderer', 'Wanderer')
    ZEALOT = Stats('zealot', 'Zealot')

    @staticmethod
    def from_id (id_):
        return _stats_id_lookup[id_]

_stats_id_lookup = _enum_id_lookup(StatsEnum)


class PvpStatsEnum (enum.Enum):
    ASSASSIN = Stats('assassin', 'Assassin')
    AVATAR = Stats('avatar', 'Avatar')
    BARBARIAN = Stats('barbarian', 'Barbarian')
    BERSERKER = Stats('berserker', 'Berserker')
    CARRION = Stats('carrion', 'Carrion')
    CAVALIER = Stats('cavalier', 'Cavalier')
    CELESTIAL = Stats('celestial', 'Celestial')
    DEADSHOT = Stats('deadshot', 'Deadshot')
    DEMOLISHER = Stats('demolisher', 'Demolisher')
    DESTROYER = Stats('destroyer', 'Destroyer')
    DIVINER = Stats('diviner', 'Diviner')
    GRIEVING = Stats('grieving', 'Grieving')
    HARRIER = Stats('harrier', 'Harrier')
    KNIGHT = Stats('knight', 'Knight')
    MARAUDER = Stats('marauder', 'Marauder')
    MARSHAL = Stats('marshal', 'Marshal')
    MENDER = Stats('mender', 'Mender')
    PALADIN = Stats('paladin', 'Paladin')
    RABID = Stats('rabid', 'Rabid')
    RAMPAGER = Stats('rampager', 'Rampager')
    SAGE = Stats('sage', 'Sage')
    SEEKER = Stats('seeker', 'Seeker')
    SINISTER = Stats('sinister', 'Sinister')
    SWASHBUCKLER = Stats('swashbuckler', 'Swashbuckler')
    VALKYRIE = Stats('valkyrie', 'Valkyrie')
    VIPER = Stats('viper', 'Viper')
    WANDERER = Stats('wanderer', 'Wanderer')
    WIZARD = Stats('wizard', 'Wizard')

    @staticmethod
    def from_id (id_):
        return _pvp_stats_id_lookup[id_]

_pvp_stats_id_lookup = _enum_id_lookup(PvpStatsEnum)


class WeaponType (_Identified):
    def __init__ (self, ids, hands):
        _Identified.__init__(self, ids)
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
        return _weapon_types_id_lookup[id_]

_weapon_types_id_lookup = _enum_id_lookup(WeaponTypes)


class WeaponHand (_Identified):
    def __init__ (self, ids, hands):
        _Identified.__init__(self, ids)
        self.hands = hands


class WeaponHands (enum.Enum):
    BOTH = WeaponHand('both', 2)
    MAIN = WeaponHand('main', 1)
    OFF = WeaponHand('off', 1)

    @staticmethod
    def from_id (id_):
        return _weapon_hands_id_lookup[id_]

_weapon_hands_id_lookup = _enum_id_lookup(WeaponHands)


class UpgradeTiers (enum.Enum):
    MINOR = 'minor'
    MAJOR = 'major'
    SUPERIOR = 'superior'


class Sigil:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier


class PvpSigil (_Identified):
    def __init__ (self, ids, name):
        _Identified.__init__(self, ids)
        self.name = name


class PvpSigils (enum.Enum):
    ABSORPTION = PvpSigil('absorption', 'Absorption')
    AGONY = PvpSigil('agony', 'Agony')
    BATTLE = PvpSigil('battle', 'Battle')
    CLEANSING = PvpSigil('cleansing', 'Cleansing')
    COMPOUNDING = PvpSigil('compounding', 'Compounding')
    CONFUSION = PvpSigil('confusion', 'Confusion')
    COURAGE = PvpSigil('courage', 'Courage')
    DOOM = PvpSigil('doom', 'Doom')
    ENERGY = PvpSigil('energy', 'Energy')
    ENHANCEMENT = PvpSigil('enhancement', 'Enhancement')
    ESCAPE = PvpSigil('escape', 'Escape')
    EXPLOITATION = PvpSigil('exploitation', 'Exploitation')
    EXPOSURE = PvpSigil('exposure', 'Exposure')
    INTELLIGENCE = PvpSigil('intelligence', 'Intelligence')
    MISERY = PvpSigil('misery', 'Misery')
    OPPORTUNITY = PvpSigil('opportunity', 'Opportunity')
    PERIL = PvpSigil('peril', 'Peril')
    PURGING = PvpSigil('purging', 'Purging')
    REVOCATION = PvpSigil('revocation', 'Revocation')
    RUTHLESSNESS = PvpSigil('ruthlessness', 'Ruthlessness')
    SAVAGERY = PvpSigil('savagery', 'Savagery')
    SEPARATION = PvpSigil('separation', 'Separation')
    SMOLDERING = PvpSigil('smoldering', 'Smoldering')
    STAGNATION = PvpSigil('stagnation', 'Stagnation')
    VENOM = PvpSigil('venom', 'Venom')

    @staticmethod
    def from_id (id_):
        return _pvp_sigils_id_lookup[id_]

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


class PvpRune (_Identified):
    def __init__ (self, ids, name):
        _Identified.__init__(self, ids)
        self.name = name


class PvpRunes (enum.Enum):
    ALTRUISM = PvpRune('altruism', 'Altruism')
    EVASION = PvpRune('evasion', 'Evasion')
    EXUBERANCE = PvpRune('exuberance', 'Exuberance')
    LEADERSHIP = PvpRune('leadership', 'Leadership')
    RADIANCE = PvpRune('radiance', 'Radiance')
    RESISTANCE = PvpRune('resistance', 'Resistance')
    SCAVENGING = PvpRune('scavenging', 'Scavenging')
    ARISTOCRACY = PvpRune('aristocracy', 'Aristocracy')
    BERSERKER = PvpRune('berserker', 'Berserker')
    CHRONOMANCER = PvpRune('chronomancer', 'Chronomancer')
    DAREDEVIL = PvpRune('daredevil', 'Daredevil')
    DRAGONHUNTER = PvpRune('dragonhunter', 'Dragonhunter')
    DRUID = PvpRune('druid', 'Druid')
    HERALD = PvpRune('herald', 'Herald')
    MAD = PvpRune('Mad', 'Mad King')
    REAPER = PvpRune('reaper', 'Reaper')
    REVENANT = PvpRune('revenant', 'Revenant')
    SCRAPPER = PvpRune('scrapper', 'Scrapper')
    SUNLESS = PvpRune('sunless', 'Sunless')
    TEMPEST = PvpRune('tempest', 'Tempest')
    TRAPPER = PvpRune('trapper', 'Trapper')
    TRAVELER = PvpRune('traveler', 'Traveler')
    THORNS = PvpRune('thorns', 'Thorns')

    @staticmethod
    def from_id (id_):
        return _pvp_runes_id_lookup[id_]

_pvp_runes_id_lookup = _enum_id_lookup(PvpRunes)


class ArmourType (_Identified):
    def __init__ (self, ids):
        _Identified.__init__(self, ids)


class ArmourTypes (enum.Enum):
    HELM = ArmourType(('helm', 'head'))
    SHOULDERS = ArmourType('shoulders')
    COAT = ArmourType(('coat', 'chest'))
    GLOVES = ArmourType(('gloves', 'hands'))
    LEGGINGS = ArmourType(('leggings', 'legs'))
    BOOTS = ArmourType(('boots', 'feet'))

    @staticmethod
    def from_id (id_):
        return _armour_types_id_lookup[id_]

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


class GearGroup (_Identified):
    def __init__ (self, ids):
        _Identified.__init__(self, ids)


class GearGroups (enum.Enum):
    WEAPONS = GearGroup('weapons')
    ARMOUR = GearGroup(('armour', 'armor'))
    TRINKETS = GearGroup('trinkets')
    ACCESSORIES = GearGroup('accessories')
    RINGS = GearGroup('rings')

    @staticmethod
    def from_id (id_):
        return _gear_groups_id_lookup[id_]

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


class RevenantLegend (_Identified):
    def __init__ (self, ids, name):
        _Identified.__init__(self, ids)
        self.name = name


class RevenantLegends (enum.Enum):
    ASSASSIN = RevenantLegend(('assassin', 'shiro'), 'Assassin')
    CENTAUR = RevenantLegend(('centaur', 'ventari'), 'Centaur')
    DEMON = RevenantLegend(('demon', 'mallyx'), 'Demon')
    DWARF = RevenantLegend(('dwarf', 'jalis'), 'Dwarf')

    DRAGON = RevenantLegend(('dragon', 'glint', 'herald'), 'Dragon')
    RENEGADE = RevenantLegend(('renegade', 'kalla'), 'Renegade')

    @staticmethod
    def from_id (id_):
        return _revenant_legends_id_lookup[id_]

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


class Boon (_Identified):
    def __init__ (self, ids, name):
        _Identified.__init__(self, ids)
        self.name = name


class Boons (enum.Enum):
    AEGIS = Boon('aegis', 'Aegis')
    ALACRITY = Boon('alacrity', 'Alacrity')
    FURY = Boon('fury', 'Fury')
    MIGHT = Boon('might', 'Might')
    PROTECTION = Boon('protection', 'Protection')
    QUICKNESS = Boon('quickness', 'Quickness')
    REGENERATION = Boon('regeneration', 'Regeneration')
    RESISTANCE = Boon('resistance', 'Resistance')
    RETALIATION = Boon('retaliation', 'Retaliation')
    STABILITY = Boon('stability', 'Stability')
    SWIFTNESS = Boon('swiftness', 'Swiftness')
    VIGOUR = Boon('vigour', 'Vigour')

    @staticmethod
    def from_id (id_):
        return _boons_id_lookup[id_]

_boons_id_lookup = _enum_id_lookup(Boons)


class BoonTarget (_Identified):
    def __init__ (self, num, name):
        _Identified.__init__(self, (str(num), name))
        self.num = num
        self.name = name


class BoonTargets (enum.Enum):
    PARTY = BoonTarget(5, 'party')
    SQUAD = BoonTarget(10, 'squad')

    @staticmethod
    def from_id (id_):
        return _boon_targets_id_lookup[id_]

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
