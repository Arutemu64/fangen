# Ruff check
ruff-check:
	ruff check src/fangen --respect-gitignore --fix

# Ruff format
ruff-format:
	ruff format src/fangen --respect-gitignore

# Type check
typecheck:
	ty check

# Lint (format + check + typecheck)
lint: ruff-format ruff-check typecheck

# Install everything (and enable the pre-commit git hook)
install:
    uv sync --all-groups
    uv run pre-commit install
