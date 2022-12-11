import json
import urllib.parse
import urllib.request

SCHEMA_VERSION = '1'


_data_by_path = {
    ('boons',): (
        {'name': 'Aegis', 'ids': ('aegis',)},
        {'name': 'Alacrity', 'ids': ('alacrity', 'alac')},
        {'name': 'Fury', 'ids': ('fury',)},
        {'name': 'Might', 'ids': ('might',)},
        {'name': 'Protection', 'ids': ('protection', 'prot')},
        {'name': 'Quickness', 'ids': ('quickness', 'quick')},
        {'name': 'Regeneration', 'ids': ('regeneration', 'regen')},
        {'name': 'Resistance', 'ids': ('resistance', 'resist')},
        {'name': 'Resolution', 'ids': ('resolution', 'reso')},
        {'name': 'Stability', 'ids': ('stability', 'stab')},
        {'name': 'Swiftness', 'ids': ('swiftness',)},
        {'name': 'Vigor', 'ids': ('vigor', 'vigour')},
    ),

    ('conditions',): (
        {'name': 'Bleeding', 'ids': ('bleeding', 'bleed')},
        {'name': 'Blind', 'ids': ('blinded', 'blind')},
        {'name': 'Burning', 'ids': ('burning', 'burn')},
        {'name': 'Chill', 'ids': ('chilled', 'chill')},
        {'name': 'Confusion', 'ids': ('confusion', 'confu')},
        {'name': 'Crippled', 'ids': ('crippled', 'cripple')},
        {'name': 'Fear', 'ids': ('fear',)},
        {'name': 'Immobilize', 'ids': (
            'immobilized', 'immobilised', 'immobilize', 'immobilise',
            'immobile', 'immob'
        )},
        {'name': 'Poison', 'ids': ('poisoned', 'poison')},
        {'name': 'Slow', 'ids': ('slow',)},
        {'name': 'Taunt', 'ids': ('taunt',)},
        {'name': 'Torment', 'ids': ('torment',)},
        {'name': 'Vulnerability', 'ids': ('vulnerability', 'vuln')},
        {'name': 'Weakness', 'ids': ('weakness',)},
    ),

    ('cc-effects',): (
        {'name': 'Daze', 'ids': ('daze', 'dazed')},
        {'name': 'Stun', 'ids': ('stun', 'stunned')},
        {'name': 'Knockdown', 'ids': ('knockdown',)},
        {'name': 'Pull', 'ids': ('pull',)},
        {'name': 'Knockback', 'ids': ('knockback', 'knock')},
        {'name': 'Launch', 'ids': ('launch',)},
        {'name': 'Float', 'ids': ('float',)},
        {'name': 'Sink', 'ids': ('sink',)},
    ),

    ('common-effects',): (
        {'name': 'Superspeed', 'ids': ('superspeed', 'ss')},
        {'name': 'Stealth', 'ids': ('stealth',)},
    )
}


class FakeClient:
    supported_paths = _data_by_path.keys()
    schema_version = SCHEMA_VERSION

    def list_ (self, path):
        return list(range(len(_data_by_path[path])))

    def get (self, path, ids):
        data = _data_by_path[path]
        for id_ in ids:
            result = dict(data[id_])
            result['id'] = id_
            yield result
