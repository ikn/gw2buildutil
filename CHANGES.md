# 0.1-next

- `api`:
    - schema version:
        - send version in requests
        - store version in storage
        - clear storage when crawling with changed version
- `defnfile`:
    - parse some text more accurately
    - map errors to `ParseError` in more cases
- use a logger

# 0.1

Initial packages:
- `defnfile`: build definition file parser
- `api`: simple API crawler and interface
- `compositions`: raids compositions generator
