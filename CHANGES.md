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
    - `entity.Skill`: add `build_id` attribute, `from_build_id` static method
- `defnfile`:
    - parse some text more accurately
    - map errors to `ParseError` in more cases
- use a logger

# 0.1 (2020-09-28)

Initial packages:
- `defnfile`: build definition file parser
- `api`: simple API crawler and interface
- `compositions`: raids compositions generator
