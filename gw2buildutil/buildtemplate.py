import logging
import base64
import struct

from . import build, api

# specification: https://en-forum.guildwars2.com/discussion/94395/api-updates-december-18-2019

logger = logging.getLogger(__name__)

_READER_FORMATS = {
    1: 'B',
    2: '<H',
    4: '<I',
}


class ParseError (ValueError):
    pass


class _Reader:
    def __init__ (self, data):
        logger.debug(f'template code bytes: {" ".join(map(str, data))}')
        self._data = data
        self._offset = 0
        self._size = len(data)

    def skip (self, size=1):
        logger.debug(f'skip {self._offset}:{size}')
        self._offset += size

    def read (self, size=1):
        if self._offset + size > self._size:
            raise ParseError(f'input too short: {self._size} bytes, '
                             f'want {self._offset + size}')

        fmt = _READER_FORMATS[size]
        value = struct.unpack_from(fmt, self._data, self._offset)[0]
        logger.debug(f'read {self._offset}:{size} -> {value}')
        self._offset += size
        return value


def _parse_profession (reader, api_storage):
    return api_storage.from_id(api.entity.Profession, reader.read())


def _parse_spec (reader, api_storage):
    spec_api_id = reader.read()
    if spec_api_id == 0:
        reader.skip()
        return None
    spec = api_storage.from_api_id(api.entity.Specialisation, spec_api_id)

    traits_data = reader.read()
    choices_indices = [
        traits_data & 0b11,
        (traits_data & 0b1100) >> 2,
        (traits_data & 0b110000) >> 4,
    ]
    choices = [
        None if n == 0 else build.TraitChoices.from_index(n - 1)
        for n in choices_indices]
    return build.SpecialisationChoices(spec, choices)


def _parse_traits (reader, api_storage):
    return build.Traits([_parse_spec(reader, api_storage) for i in range(3)])


def _parse_skill (reader, profession, api_storage):
    build_id = reader.read(2)
    if build_id == 0:
        return None
    else:
        return api.entity.Skill.from_build_id(profession, build_id, api_storage)


def _parse_skills (reader, profession, api_storage):
    skills = [_parse_skill(reader, profession, api_storage) for i in range(10)]
    terrestrial_skills = build.Skills(
        skills[0], [skills[2], skills[4], skills[6]], skills[8])
    aquatic_skills = build.Skills(
        skills[1], [skills[3], skills[5], skills[7]], skills[9])
    return (terrestrial_skills, aquatic_skills)


def _parse_revenant_legend (reader, api_storage):
    build_id = reader.read()
    if build_id == 0:
        return None
    else:
        return api_storage.from_id(api.entity.RevenantLegend, build_id)


def _parse_revenant_skills (reader, api_storage):
    reader.skip(2 * 5 * 2) # normal skills
    legends = [_parse_revenant_legend(reader, api_storage) for i in range(4)]
    reader.skip(2 * 3 * 2) # legend skill order
    return (build.RevenantSkills(legends[:2]),
            build.RevenantSkills(legends[2:]))


def _parse_ranger_pet (reader, api_storage):
    api_id = reader.read()
    if api_id == 0:
        return None
    else:
        return api_storage.from_api_id(api.entity.RangerPet, api_id)


def _parse_ranger_pets (reader, api_storage):
    pets = [_parse_ranger_pet(reader, api_storage) for i in range(4)]
    return (build.RangerPets(pets[:2]), build.RangerPets(pets[2:]))


def parse (code, api_storage):
    if len(code) < 3 or code[:2] != '[&' or code[-1] != ']':
        raise ParseError('invalid format')
    reader = _Reader(base64.b64decode(code[2:-1]))
    if reader.read() != 0xd:
        raise ParseError('invalid format')

    prof = _parse_profession(reader, api_storage)
    traits = _parse_traits(reader, api_storage)
    if prof.id_ == 'revenant':
        skills, aquatic_skills = _parse_revenant_skills(reader, api_storage)
    else:
        skills, aquatic_skills = _parse_skills(reader, prof, api_storage)
    if prof.id_ == 'ranger':
        pets, aquatic_pets = _parse_ranger_pets(reader, api_storage)
        prof_opts = build.RangerOptions(pets, aquatic_pets)
    else:
        prof_opts = None

    elite_spec = None
    for spec in traits.specs:
        if spec is not None and spec.spec.is_elite:
            elite_spec = spec
    meta = build.BuildMetadata(None, prof, elite_spec)
    intro = build.Intro(None, None, None,
                        traits, skills, prof_opts, aquatic_skills)
    return build.Build(meta, intro)
