class GameModes:
    def __init__ (self, name, game_modes):
        self.name = name
        self.game_modes = set(game_modes)

    def __str__ (self):
        return self.name

    @property
    def description (self):
        return 'Builds intended for use in game modes: {}.'.format(
            ', '.join(self.game_modes))


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

    def __str__ (self):
        return '<WeaponHand({})>'.format(self.label)

    __repr__ = __str__


class Sigil:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier

    def __str__ (self):
        return '{} sigil of {}'.format(tier, name)


class Weapon:
    def __init__ (self, type_, hand, stat, sigils):
        self.type_ = type_
        self.hand = hand
        self.stat = stat
        self.sigils = tuple(sigils)

        if len(self.sigils) != len(self.hand):
            raise ValueError('wrong number of sigils for ' \
                             '{}: {}'.format(self.hand, len(self.sigils)))


class Weapons:
    def __init__ (self, set1, set2=None):
        self.set1 = tuple(set1)
        self.set2 = None if set2 is None else tuple(set2)

        if sum(len(w.hand) for w in self.set1) != 2:
            raise ValueError('wrong number of weapons in set 1: ' \
                            '{}'.format(self.set1))
        if self.set2 is not None and sum(len(w.hand) for w in self.set2) != 2:
            raise ValueError('wrong number of weapons in set 2: ' \
                            '{}'.format(self.set1))


class Rune:
    def __init__ (self, name, tier):
        self.name = name
        self.tier = tier

    def __str__ (self):
        return '{} rune of {}'.format(tier, name)


class ArmourPiece:
    def __init__ (self, type_, stat, rune):
        self.type_ = type_
        self.stat = stat
        self.rune = rune


class Armour:
    def __init__ (self, pieces):
        self.pieces = {p.type_: p for p in pieces}

        if len(pieces) != 6:
            raise ValueError('expected 6 armour pieces, got ' \
                             '{}'.format(len(pieces)))
        if len(self.pieces) != 6:
            raise ValueError('not all armour types are present: ' \
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


class Build:
    def __init__ (self, metadata, intro, alternatives=None, usage=None,
                  notes=None, encounters=None):
        self.metadata = metadata
        self.intro = intro
        self.alternatives = alternatives
        self.usage = usage
        self.notes = notes
        self.encounters = encounters
