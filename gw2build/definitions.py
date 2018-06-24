from . import build

game_modes = {
    'raids': build.GameModes(
        'Raids', ('raids', 'organised fractals')),
    'fractals': build.GameModes(
        'Fractals', ('unorganised fractals', 'dungeons', 'open world')),
    'dungeons': build.GameModes(
        'Dungeons', ('dungeons', 'open world')),
    'open world': build.GameModes(
        'Open World', ('open world',)),
    'pvp': build.GameModes(
        'PvP', ('PvP',)),
    'wvw': build.GameModes(
        'WvW', ('WvW',)),
}

profession = {
    'warrior': build.Profession('Warrior'),
    'berserker': build.Profession('Warrior', 'Berserker'),
    'spellbreaker': build.Profession('Warrior', 'Spellbreaker'),
    'guardian': build.Profession('Guardian'),
    'dragonhunter': build.Profession('Guardian', 'Dragonhunter'),
    'firebrande': build.Profession('Guardian', 'Firebrand'),
    'revenant': build.Profession('Revenant'),
    'herald': build.Profession('Revenant', 'Herald'),
    'renegade': build.Profession('Revenant', 'Renegade'),
    'ranger': build.Profession('Ranger'),
    'druid': build.Profession('Ranger', 'Druid'),
    'soulbeast': build.Profession('Ranger', 'Soulbeast'),
    'thief': build.Profession('Thief'),
    'daredevil': build.Profession('Thief', 'Daredevil'),
    'deadeye': build.Profession('Thief', 'Deadeye'),
    'engineer': build.Profession('Engineer'),
    'scrapper': build.Profession('Engineer', 'Scrapper'),
    'holosmith': build.Profession('Engineer', 'Holosmith'),
    'necromancer': build.Profession('Necromancer'),
    'reaper': build.Profession('Necromancer', 'Reaper'),
    'scourge': build.Profession('Necromancer', 'Scourge'),
    'elementalist': build.Profession('Elementalist'),
    'tempest': build.Profession('Elementalist', 'Tempest'),
    'weaver': build.Profession('Elementalist', 'Weaver'),
    'mesmer': build.Profession('Mesmer'),
    'chronomancer': build.Profession('Mesmer', 'Chronomancer'),
    'mirage': build.Profession('Mesmer', 'Mirage'),
}

weapon_type = {
    'greatsword': 'greatsword',
    'hammer': 'hammer',
    'longbow': 'longbow',
    'rifle': 'rifle',
    'shortbow': 'shortbow',
    'staff': 'staff',

    'axe': 'axe',
    'dagger': 'dagger',
    'mace': 'mace',
    'pistol': 'pistol',
    'sword': 'sword',
    'sceptre': 'sceptre',
    'scepter': 'sceptre',
    'focus': 'focus',
    'shield': 'shield',
    'torch': 'torch',
    'warhorn': 'warhorn',

    'harpoon': 'harpoon',
    'spear': 'spear',
    'trident': 'trident',
}

weapon_hand = {
    'both': build.WeaponHand(True, True),
    'main': build.WeaponHand(True, False),
    'off': build.WeaponHand(False, True),
}

upgrade_tier = {
    'superior': 'superior',
    'major': 'major',
    'minor': 'minor',
}

armour_type = {
    'helm': 'helm',
    'head': 'helm',
    'shoulders': 'shoulders',
    'coat': 'coat',
    'chest': 'coat',
    'gloves': 'gloves',
    'hands': 'gloves',
    'leggings': 'leggings',
    'legs': 'leggings',
    'boots': 'boots',
    'feet': 'boots',
}
