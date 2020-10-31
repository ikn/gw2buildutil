import logging
import base64
import struct

from . import build as gw2build, api

# specification: https://en-forum.guildwars2.com/discussion/94395/api-updates-december-18-2019

logger = logging.getLogger(__name__)

_READER_FORMATS = {
    1: 'B',
    2: '<H',
    4: '<I',
}
_SKILLS_SIZE = 2 * 5 * 2
_LEGEND_SKILLS_SIZE = 2 * 3 * 2
_LEGENDS_TOTAL_SIZE = 2 * 2 * 1 + _LEGEND_SKILLS_SIZE
_PETS_SIZE = 2 * 2 * 1
_SUFFIX_SIZE = max(_LEGENDS_TOTAL_SIZE, _PETS_SIZE)


# some build IDs map to unexpected skills - this is a list of overrides
_SKILL_FIXES = (
    {'build id': 5958, 'api id': 45449}, # Jaunt / Mirage Mirror
)
_SKILL_API_IDS = {fix['build id']: fix['api id'] for fix in _SKILL_FIXES}
_SKILL_BUILD_IDS = {fix['api id']: fix['build id'] for fix in _SKILL_FIXES}


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
    try:
        return api_storage.from_id(api.entity.Profession, reader.read())
    except KeyError:
        raise ParseError('invalid profession ID')


def _parse_spec (reader, api_storage):
    spec_api_id = reader.read()
    if spec_api_id == 0:
        reader.skip()
        return None
    try:
        spec = api_storage.from_api_id(api.entity.Specialisation, spec_api_id)
    except KeyError:
        raise ParseError('invalid specialisation ID')

    traits_data = reader.read()
    choices_indices = [
        traits_data & 0b11,
        (traits_data & 0b1100) >> 2,
        (traits_data & 0b110000) >> 4,
    ]
    choices = [
        None if n == 0 else gw2build.TraitChoices.from_index(n - 1)
        for n in choices_indices]
    return gw2build.SpecialisationChoices(spec, choices)


def _parse_traits (reader, api_storage):
    return gw2build.Traits([_parse_spec(reader, api_storage) for i in range(3)])


def _parse_skill (reader, profession, api_storage):
    build_id = reader.read(2)
    if build_id == 0:
        return None
    elif build_id in _SKILL_API_IDS:
        return api_storage.from_api_id(api.entity.Skill,
                                       _SKILL_API_IDS[build_id])
    else:
        return api.entity.Skill.from_build_id(profession, build_id, api_storage)


def _parse_skills (reader, profession, api_storage):
    skills = [_parse_skill(reader, profession, api_storage) for i in range(10)]
    terrestrial_skills = gw2build.Skills(
        skills[0], [skills[2], skills[4], skills[6]], skills[8])
    aquatic_skills = gw2build.Skills(
        skills[1], [skills[3], skills[5], skills[7]], skills[9])
    return (terrestrial_skills, aquatic_skills)


def _parse_revenant_legend (reader, api_storage):
    build_id = reader.read()
    if build_id == 0:
        return None
    else:
        try:
            return api_storage.from_id(api.entity.RevenantLegend, build_id)
        except KeyError:
            raise ParseError('invalid legend ID')


def _parse_revenant_skills (reader, api_storage):
    legends = [_parse_revenant_legend(reader, api_storage) for i in range(4)]
    reader.skip(_LEGEND_SKILLS_SIZE)
    return (gw2build.RevenantSkills(legends[:2]),
            gw2build.RevenantSkills(legends[2:]))


def _parse_ranger_pet (reader, api_storage):
    api_id = reader.read()
    if api_id == 0:
        return None
    else:
        try:
            return api_storage.from_api_id(api.entity.RangerPet, api_id)
        except KeyError:
            raise ParseError('invalid pet ID')


def _parse_ranger_pets (reader, api_storage):
    pets = [_parse_ranger_pet(reader, api_storage) for i in range(4)]
    return (gw2build.RangerPets(pets[:2]), gw2build.RangerPets(pets[2:]))


def parse (code, api_storage):
    if len(code) < 3 or code[:2] != '[&' or code[-1] != ']':
        raise ParseError('invalid format')
    reader = _Reader(base64.b64decode(code[2:-1]))
    if reader.read() != 0xd:
        raise ParseError('invalid format')

    prof = _parse_profession(reader, api_storage)
    traits = _parse_traits(reader, api_storage)
    if prof.id_ == 'revenant':
        reader.skip(_SKILLS_SIZE)
    else:
        skills, aquatic_skills = _parse_skills(reader, prof, api_storage)

    if prof.id_ == 'revenant':
        skills, aquatic_skills = _parse_revenant_skills(reader, api_storage)
    if prof.id_ == 'ranger':
        pets, aquatic_pets = _parse_ranger_pets(reader, api_storage)
        prof_opts = gw2build.RangerOptions(pets, aquatic_pets)
    else:
        prof_opts = None

    elite_spec = None
    for spec_choices in traits.specs:
        if spec_choices is not None and spec_choices.spec.is_elite:
            elite_spec = spec_choices.spec
    meta = gw2build.BuildMetadata(None, prof, elite_spec)
    intro = gw2build.Intro(None, None, None,
                        traits, skills, prof_opts, aquatic_skills)
    return gw2build.Build(meta, intro)


def _render_profession (build):
    return [build.metadata.profession.build_id]


def _render_spec (spec_choices):
    if spec_choices is None:
        return [0, 0]

    choices_data = [0 if choice is None else (choice.value.index + 1)
                    for choice in spec_choices.choices]
    return [
        spec_choices.spec.api_id,
        choices_data[0] | (choices_data[1] << 2) | (choices_data[2] << 4),
    ]


def _render_traits (build):
    data = []
    # elite spec must come last
    specs = sorted(build.intro.traits.specs,
                   key=lambda spec_choices: spec_choices.spec.is_elite)
    for spec_choices in specs:
        data.extend(_render_spec(spec_choices))
    return data


def _render_skill (skill):
    if skill is not None:
        if skill.build_id is not None:
            build_id = skill.build_id
        elif skill.api_id in _SKILL_BUILD_IDS:
            build_id = _SKILL_BUILD_IDS[skill.api_id]
        else:
            raise ValueError('build cannot be rendered to a template code: '
                             f'skill has no build ID: {skill.name}')
    else:
        build_id = 0
    return struct.pack(_READER_FORMATS[2], build_id)


def _render_skills (build):
    aquatic_skills = (gw2build.Skills(None, (None, None, None), None)
                      if build.intro.aquatic_skills is None
                      else build.intro.aquatic_skills)

    skills = [
        build.intro.skills.heal,
        aquatic_skills.heal,
        build.intro.skills.utilities[0],
        aquatic_skills.utilities[0],
        build.intro.skills.utilities[1],
        aquatic_skills.utilities[1],
        build.intro.skills.utilities[2],
        aquatic_skills.utilities[2],
        build.intro.skills.elite,
        aquatic_skills.elite,
    ]

    data = []
    for skill in skills:
        data.extend(_render_skill(skill))
    return data


def _render_revenant_legends (build):
    data = []

    for skills in (build.intro.skills, build.intro.aquatic_skills):
        if skills is None:
            data.extend([0] * 2 * 1)
        else:
            for legend in skills.legends:
                data.append(0 if legend is None else legend.build_id)

    # legend skill order not currently stored in the build
    data.extend([0] * _LEGEND_SKILLS_SIZE)

    return data


def _render_ranger_pets (build):
    data = []
    for pets in (
        build.intro.profession_options.pets,
        build.intro.profession_options.aquatic_pets,
    ):
        if pets is None:
            data.extend([0] * 2)
        else:
            for pet in pets.pets:
                data.append(0 if pet is None else pet.api_id)
    return data


def render (build):
    data = []
    data.append(0xd)
    data.extend(_render_profession(build))
    data.extend(_render_traits(build))
    if build.metadata.profession.id_ == 'revenant':
        data.extend([0] * _SKILLS_SIZE)
    else:
        data.extend(_render_skills(build))

    if build.metadata.profession.id_ == 'revenant':
        data.extend(_render_revenant_legends(build))
        data.extend([0] * (_SUFFIX_SIZE - _LEGENDS_TOTAL_SIZE))
    elif build.metadata.profession.id_ == 'ranger':
        data.extend(_render_ranger_pets(build))
        data.extend([0] * (_SUFFIX_SIZE - _PETS_SIZE))
    else:
        data.extend([0] * _SUFFIX_SIZE)

    code = base64.b64encode(bytes(data)).decode('ascii')
    return f'[&{code}]'
