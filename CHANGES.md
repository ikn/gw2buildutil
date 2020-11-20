# 0.4

- `build`:
    - **breaking**: remove `MarkdownBody`
    - add more trait stuff: `TraitTier` (`TraitTiers`), `TraitType`
      (`TraitTypes`), `TraitChoices.from_api_id`
- `api`:
    - add `entity.Trait`
    - `entity.Entity`: add `extra_entity_relations` method for overriding
    - `Skill` entities are now indexed by extra IDs:
        - weapon skills, eg. `pistol 4`, `gs 3`, `dagger earth 5`,
          `elixir gun 4`, `staff ambush`, `sword stealth`, `sword dagger 3`
        - profession skills, eg. `f3`, `scrapper f5`
        - engineer toolbelt skills, eg. `elixir h toolbelt`, `bk tb`
        - legend skills, eg. `assassin heal`, `jalis elite`
    - `entity.Skill`: add `is_flipover`, `filter_is_main`, `profession`
    - `Profession` and `Specialisation` entities are now indexed by abbreviated
      IDs, eg. `necro`, `holo`
    - `storage.Storage.from_id` can now be called with multiple entity types
    - **breaking**: change `entity.RevenantLegend` attributes to methods:
      `heal_skill`, `utility_skills`, `elite_skill`
    - **breaking**: move `Filters` from `storage` to `util`, and change
      constructor to require instances of the new `util.Filter` class
    - **breaking**: some entity filters are now static methods instead of class
      attributes: `Skill.filter_has_build_id`, `Skill.filter_is_main`,
      `Stats.filter_endgame`, `Stats.filter_not_mixed`
- `textbody`: new module
- `defnfile`:
    - parse `usage` and `notes` sections

# 0.3

- `build`:
    - perform a lot more validation when constructing instances
    - add `SkillType` and `SkillTypes`
    - throw `BuildError` instead of `ValueError`
    - **breaking**: remove aquatic weapon types until they're properly supported
- `api`:
    - `entity.Profession`: add `can_wield` method
    - `entity.Skill`: add `type_`, `professions`, `elite_spec`, `weapon_type`,
      `is_aquatic`, `filter_has_build_id`, `filter_profession`,
      `filter_elite_spec` and `filter_type` attributes
    - `entity.Stats`: add `filter_endgame` and `filter_not_mixed` attributes
    - **breaking**: remove `entity.Entity.from_api` - now implement using
      subclass constructors
    - **breaking**: remove `entity.Entity.filter`
    - **breaking**: change `filters` argument to `storage.Storage.from_id` to a
      `storage.Storage.Filters` object
- `defnfile`:
    - allow skill abbreviations that were previously ambiguous by filtering to
      the current context (uses skill type, profession and elite spec)
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
