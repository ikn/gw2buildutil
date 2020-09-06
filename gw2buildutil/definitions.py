from . import build

game_modes = {
    'open world': build.GameModes(
        'Open World', ('open world', 'dungeons')),
    'dungeons': build.GameModes(
        'Dungeons', ('dungeons',)),
    'fractals': build.GameModes(
        'Fractals', ('unorganised fractals', 'dungeons', 'open world')),
    'raids': build.GameModes(
        'Raids', ('casual raids', 'casual organised fractals')),
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
    'firebrand': build.Profession('Guardian', 'Firebrand'),
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
    'minor': 'minor',
    'major': 'major',
    'superior': 'superior',
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
    'apothecary': build.Stats('Apothecary'),
    'assassin': build.Stats('Assassin'),
    'berserker': build.Stats('Berserker'),
    'bringer': build.Stats('Bringer'),
    'captain': build.Stats('Captain'),
    'carrion': build.Stats('Carrion'),
    'cavalier': build.Stats('Cavalier'),
    'celestial': build.Stats('Celestial'),
    'cleric': build.Stats('Cleric'),
    'commander': build.Stats('Commander'),
    'crusader': build.Stats('Crusader'),
    'dire': build.Stats('Dire'),
    'diviner': build.Stats('Diviner'),
    'giver': build.Stats('Giver'),
    'grieving': build.Stats('Grieving'),
    'harrier': build.Stats('Harrier'),
    'knight': build.Stats('Knight'),
    'magi': build.Stats('Magi'),
    'marauder': build.Stats('Marauder'),
    'marshal': build.Stats('Marshal'),
    'minstrel': build.Stats('Minstrel'),
    'nomad': build.Stats('Nomad'),
    'plaguedoctor': build.Stats('Plaguedoctor'),
    'rabid': build.Stats('Rabid'),
    'rampager': build.Stats('Rampager'),
    'sentinel': build.Stats('Sentinel'),
    'seraph': build.Stats('Seraph'),
    'settler': build.Stats('Settler'),
    'shaman': build.Stats('Shaman'),
    'sinister': build.Stats('Sinister'),
    'soldier': build.Stats('Soldier'),
    'trailblazer': build.Stats('Trailblazer'),
    'valkyrie': build.Stats('Valkyrie'),
    'vigilant': build.Stats('Vigilant'),
    'viper': build.Stats('Viper'),
    'wanderer': build.Stats('Wanderer'),
    'zealot': build.Stats('Zealot'),
}

pvp_stats = {
    'assassin': build.Stats('Assassin'),
    'avatar': build.Stats('Avatar'),
    'barbarian': build.Stats('Barbarian'),
    'berserker': build.Stats('Berserker'),
    'carrion': build.Stats('Carrion'),
    'cavalier': build.Stats('Cavalier'),
    'celestial': build.Stats('Celestial'),
    'deadshot': build.Stats('Deadshot'),
    'demolisher': build.Stats('Demolisher'),
    'destroyer': build.Stats('Destroyer'),
    'diviner': build.Stats('Diviner'),
    'grieving': build.Stats('Grieving'),
    'harrier': build.Stats('Harrier'),
    'knight': build.Stats('Knight'),
    'marauder': build.Stats('Marauder'),
    'marshal': build.Stats('Marshal'),
    'mender': build.Stats('Mender'),
    'paladin': build.Stats('Paladin'),
    'rabid': build.Stats('Rabid'),
    'rampager': build.Stats('Rampager'),
    'sage': build.Stats('Sage'),
    'seeker': build.Stats('Seeker'),
    'sinister': build.Stats('Sinister'),
    'swashbuckler': build.Stats('Swashbuckler'),
    'valkyrie': build.Stats('Valkyrie'),
    'viper': build.Stats('Viper'),
    'wanderer': build.Stats('Wanderer'),
    'wizard': build.Stats('Wizard'),
}

boons = {
    'aegis': build.Boon('aegis', 'Aegis'),
    'alacrity': build.Boon('alacrity', 'Alacrity'),
    'fury': build.Boon('fury', 'Fury'),
    'might': build.Boon('might', 'Might'),
    'protection': build.Boon('protection', 'Protection'),
    'quickness': build.Boon('quickness', 'Quickness'),
    'regeneration': build.Boon('regeneration', 'Regeneration'),
    'resistance': build.Boon('resistance', 'Resistance'),
    'retaliation': build.Boon('retaliation', 'Retaliation'),
    'stability': build.Boon('stability', 'Stability'),
    'swiftness': build.Boon('swiftness', 'Swiftness'),
    'vigour': build.Boon('vigour', 'Vigour'),
}

boon_targets = {
    '5': build.BoonTarget('party'),
    '10': build.BoonTarget('squad'),
}
