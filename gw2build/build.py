class GameModes:
    def __init__ (self, name, game_modes):
        self.name = name
        self.game_modes = list(game_modes)

    @property
    def description (self):
        return 'Builds intended for use in game modes: {}.'.format(
            ', '.join(self.game_modes))

    def __str__ (self):
        return self.name


class Profession:
    def __init__ (self, profession, elite_spec=None):
        self.profession = profession
        self.elite_spec = elite_spec

    def __str__ (self):
        return self.profession if self.elite_spec is None else self.elite_spec


class BuildMetadata:
    def __init__ (self, game_modes, profession, labels):
        self.game_modes = game_modes
        self.profession = profession
        self.labels = tuple(labels)

    @property
    def title (self):
        return '{} {}: {}'.format(self.game_modes, self.profession,
                                  ', '.join(self.labels))


class TextBody:
    pass


class MarkdownBody (TextBody):
    def __init__ (self, text):
        self.text = text


class Stats:
    def __init__ (self, name):
        self.name = name


class WeaponHand:
    def __init__ (self, main, off):
        self.main = bool(main)
        self.off = bool(off)

        if not self.main and not self.off:
            raise ValueError('cannot have a weapon with no hand assignment')

    def __len__ (self):
        return int(self.main) + int(self.off)

    @property
    def label (self):
        if self.main and self.off:
            return 'both'
        elif self.main:
            return 'main'
        else:
            return 'off'


class Sigil:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier


class Weapon:
    def __init__ (self, type_, hand, stats, sigils):
        self.type_ = type_
        self.hand = hand
        self.stats = stats
        self.sigils = tuple(sigils)

        if len(self.sigils) != len(self.hand):
            raise ValueError('wrong number of sigils for '
                             '{}: {}'.format(self.hand, len(self.sigils)))


class Weapons:
    def __init__ (self, set1, set2=None):
        self.set1 = tuple(set1)
        self.set2 = None if set2 is None else tuple(set2)

        if sum(len(w.hand) for w in self.set1) != 2:
            raise ValueError('wrong number of weapons in set 1: '
                            '{}'.format(self.set1))
        if self.set2 is not None and sum(len(w.hand) for w in self.set2) != 2:
            raise ValueError('wrong number of weapons in set 2: '
                            '{}'.format(self.set1))


class Rune:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier


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


class Gear:
    def __init__ (self, weapons, armour, trinkets, consumables):
        self.weapons = weapons
        self.armour = armour
        self.trinkets = trinkets
        self.consumables = consumables


class Intro:
    def __init__ (self, url, description, gear, traits, skills,
                  profession_options=None):
        self.url = url
        self.description = description
        self.gear = gear
        self.traits = traits
        self.skills = skills
        self.profession_options = None


class Boon:
    def __init__ (self, id_, name):
        self.id_ = id_
        self.name = name


class BoonTarget:
    def __init__ (self, name):
        self.name = name


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
