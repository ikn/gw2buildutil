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


class Build:
    pass
