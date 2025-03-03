# Contribution

All contributions are welcome!

## Reporting issues
If you find any issues or have any suggestions, please open an issue on the [GitHub issue tracker](https://github.com/austinyu/ujson5/issues). Please provide as much information as possible, including the version of `ujson5` you are using, the version of Python you are using, and the platform you are on.

## Contributing code

### Setup development environment

- Install [poetry](https://python-poetry.org/docs/)
- `poetry install --with dev`
- `pre-commit install`

### CLIs

- `poetry install --with [group]`
- `poetry add --group [group] [dep]`
- `mkdocs server`

## Future work

- CLI implementation
- versioning docs using `mike`
- add optional arg to encode to cache comments in frozen or optimized mode
- makefile automation
- doc-test
