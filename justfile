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

# Build exe (onedir) from the committed PyInstaller spec
build-exe:
    uv run pyinstaller fangen.spec --clean --noconfirm

# Bundle release: exe + user-facing config/dictionary, zipped
bundle-exe: build-exe
    cp config.dist.toml ./dist/fangen/config.toml
    cp dictionary.json ./dist/fangen/dictionary.json
    cd dist && rm -f release.zip
    cd dist && 7z a release.zip ./fangen


