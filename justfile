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

# Build exe
build-exe:
    pyinstaller src/fangen/__main__.py -n fangen

# Bundle release
bundle-exe: build-exe
    cp config.dist.toml ./dist/config.toml
    cp dictionary.json ./dist/dictionary.json
    cd dist && rm -f release.zip
    cd dist && cp -r ./fangen/. ./
    cd dist && 7z a release.zip fangen.exe config.toml dictionary.json _internal


