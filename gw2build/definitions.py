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

trinket_type = {
    'back': 'back',
    'accessory 1': 'accessory 1',
    'accessory 2': 'accessory 2',
    'amulet': 'amulet',
    'ring 1': 'ring 1',
    'ring 2': 'ring 2',
}

gear_group = {
    'weapons': 'weapon',
    'armour': 'armour',
    'trinkets': 'trinket',
    'accessories': 'accessory',
    'rings': 'ring',
}
gear_group.update(weapon_type)
gear_group.update(armour_type)
gear_group.update(trinket_type)

stats = {
    'berserker': build.Stats('Berserker'),
    'zealot': build.Stats('Zealot'),
    'soldier': build.Stats('Soldier'),
    'valkyrie': build.Stats('Valkyrie'),
    'captain': build.Stats('Captain'),
    'rampager': build.Stats('Rampager'),
    'assassin': build.Stats('Assassin'),
    'knight': build.Stats('Knight'),
    'cavalier': build.Stats('Cavalier'),
    'nomad': build.Stats('Nomad'),
    'giver': build.Stats('Giver'),
    'settler': build.Stats('Settler'),
    'sentinel': build.Stats('Sentinel'),
    'shaman': build.Stats('Shaman'),
    'sinister': build.Stats('Sinister'),
    'carrion': build.Stats('Carrion'),
    'rabid': build.Stats('Rabid'),
    'dire': build.Stats('Dire'),
    'cleric': build.Stats('Cleric'),
    'magi': build.Stats('Magi'),
    'apothecary': build.Stats('Apothecary'),
    'bringer': build.Stats('Bringer'),
    'harrier': build.Stats('Harrier'),
    'commander': build.Stats('Commander'),
    'marauder': build.Stats('Marauder'),
    'vigilant': build.Stats('Vigilant'),
    'crusader': build.Stats('Crusader'),
    'wanderer': build.Stats('Wanderer'),
    'viper': build.Stats('Viper'),
    'seraph': build.Stats('Seraph'),
    'trailblazer': build.Stats('Trailblazer'),
    'minstrel': build.Stats('Minstrel'),
    'grieving': build.Stats('Grieving'),
    'marshal': build.Stats('Marshal'),
    'plaguedoctor': build.Stats('Plaguedoctor'),
    'celestial': build.Stats('Celestial'),
}

pvp_stats = {
    'berserker': build.Stats('Berserker'),
    'valkyrie': build.Stats('Valkyrie'),
    'rampager': build.Stats('Rampager'),
    'assassin': build.Stats('Assassin'),
    'knight': build.Stats('Knight'),
    'cavalier': build.Stats('Cavalier'),
    'barbarian': build.Stats('Barbarian'),
    'sinister': build.Stats('Sinister'),
    'carrion': build.Stats('Carrion'),
    'rabid': build.Stats('Rabid'),
    'harrier': build.Stats('Harrier'),
    'paladin': build.Stats('Paladin'),
    'demolisher': build.Stats('Demolisher'),
    'seeker': build.Stats('Seeker'),
    'destroyer': build.Stats('Destroyer'),
    'diviner': build.Stats('Diviner'),
    'sage': build.Stats('Sage'),
    'mender': build.Stats('Mender'),
    'deadshot': build.Stats('Deadshot'),
    'marauder': build.Stats('Marauder'),
    'wanderer': build.Stats('Wanderer'),
    'viper': build.Stats('Viper'),
    'swashbuckler': build.Stats('Swashbuckler'),
    'avatar': build.Stats('Avatar'),
    'grieving': build.Stats('Grieving'),
    'wizard': build.Stats('Wizard'),
    'marshal': build.Stats('Marshal'),
    'celestial': build.Stats('Celestial'),
}
