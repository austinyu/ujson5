# .DEFAULT_GOAL := all
sources = src tests

.PHONY: .uv  ## Check that uv is installed
.uv:
	@uv -V || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: .pre-commit  ## Check that pre-commit is installed
.pre-commit: .uv
	@uv run pre-commit -V || uv pip install pre-commit

.PHONY: install  ## Install the package, dependencies, and pre-commit for local development
install: .uv
	uv sync --frozen --group all --all-extras
	uv pip install pre-commit
	uv run pre-commit install --install-hooks

.PHONY: rebuild-lockfiles  ## Rebuild lockfiles from scratch, updating all dependencies
rebuild-lockfiles: .uv
	uv lock --upgrade

.PHONY: format  ## Auto-format python source files
format: .uv
	uv run pre-commit run trailing-whitespace
	uv run pre-commit run end-of-file-fixer
	uv run black $(sources)

.PHONY: lint  ## Lint python source files
lint: .uv
	uv run flake8 $(sources)
	uv run pylint $(sources)

.PHONY: cspell  ## Use cspell to do spellchecking
cspell: .pre-commit
	uv run pre-commit run cspell

.PHONY: typecheck  ## Perform type-checking
typecheck: .uv
	uv run mypy $(sources)

.PHONY: test  ## Run all tests, skipping the type-checker integration tests
test: .uv
	uv run pytest

.PHONY: all  ## Run the standard set of checks performed in CI
all: format lint typecheck cspell test

.PHONY: clean  ## Clear local caches and build artifacts
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -rf site
	rm -rf docs/_build
	rm -rf docs/.changelog.md docs/.version.md docs/.tmp_schema_mappings.html
	rm -rf fastapi/test.db
	rm -rf coverage.xml

.PHONY: docs  ## Generate the docs
docs:
	uv run mkdocs build --strict

# .PHONY: help  ## Display this message
# help:
# 	@grep -E \
# 		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
# 		sort | \
# 		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
