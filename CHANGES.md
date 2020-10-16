# 0.2-next

- `build`:
    - perform a lot more validation when constructing instances
    - add `SkillType` and `SkillTypes`
    - throw `BuildError` instead of `ValueError`
    - **breaking**: remove aquatic weapon types until they're properly supported
- `api`:
    - `entity.Profession`: add `can_wield` method
    - `entity.Skill`: add `type_`, `professions`, `weapon_type` and `is_aquatic`
      attributes
    - **breaking**: remove `entity.Entity.from_api` - now implement using
      subclass constructors
- `buildtemplate`:
    - fix bug: parsing would set `BuildMetadata.elite_spec` to a
      `SpecialisationChoices` instance instead of a `Specialisation` instance
- implement `__str__`, `__repr__`, `__eq__` and `__hash__` where appropriate for
  classes in `build` and `api.entity`

# 0.2 (2020-10-08)

- `buildtemplate`: new module
- `api`:
    - add optional `filters` argument to `Storage.from_id()`, and improve
      default lookup behaviour
    - schema version:
        - send version in requests
        - store version in storage
        - clear storage when crawling with changed version
    - **breaking**: remove `storage.Storage.exists()`
    - **breaking**: remove `non_unique_ids` argument from `Entity()`; remove
      `aliases` attribute from `Entity`
    - add `entity.RevenantLegend`
        - **breaking**: moved from an enum in `build`
        - add attributes: `build_id`, `heal_skill`, `utility_skills`,
          `elite_skill`
    - `entity.Profession`: add `build_id` attribute
    - `entity.Skill`: add `build_id` attribute, `from_build_id()` static method
    - **breaking**: `entity.Entity`: change `from_api()` argument order
- `build`:
    - add aquatic variants for skills, legends and pets
    - **breaking**: for ranger, `Intro.profession_options` is now
      `RangerOptions` instead of `RangerPets`
- `defnfile`:
    - parse some text more accurately
    - map errors to `ParseError` in more cases
- use a logger

# 0.1 (2020-09-28)

Initial packages:
- `defnfile`: build definition file parser
- `api`: simple API crawler and interface
- `compositions`: raids compositions generator
