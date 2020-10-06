# 0.1-next

- `api`:
    - schema version:
        - send version in requests
        - store version in storage
        - clear storage when crawling with changed version
    - add `entity.RevenantLegend`
        - **breaking**: moved from an enum in `build`
        - add `build_id` attribute
    - `entity.Profession`: add `build_id` attribute
    - `entity.Skill`: add `build_id` attribute, `from_build_id()` static method
    - **breaking**: `entity.Entity`: change `from_api()` argument order
    - **breaking**: remove `storage.Storage.exists()`
    - add optional `filters` argument to `Storage.from_id()`, and improve
      default lookup behaviour
    - **breaking**: remove `non_unique_ids` argument from `Entity()`; remove
      `aliases` attribute from `Entity`
- `defnfile`:
    - parse some text more accurately
    - map errors to `ParseError` in more cases
- `build`:
    - added aquatic variants for skills, legends and pets
    - **breaking**: for ranger, `Intro.profession_options` is now
      `RangerOptions` instead of `RangerPets`
- `buildtemplate`: new module
- use a logger

# 0.1 (2020-09-28)

Initial packages:
- `defnfile`: build definition file parser
- `api`: simple API crawler and interface
- `compositions`: raids compositions generator
