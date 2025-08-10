# Ruff check
ruff-check:
	ruff check src/fangen --respect-gitignore --fix

# Ruff format
ruff-format:
	ruff format src/fangen --respect-gitignore

# Lint (format + check)
lint: ruff-format ruff-check

# Install everything
install:
    uv sync --all-groups

# Build exe
build-exe:
    pyinstaller src/fangen/__main__.py --onefile -n fangen

# Bundle release
bundle-exe: build-exe
    cp config.dist.toml ./dist/config.toml
    cp dictionary.json ./dist/dictionary.json
    cd dist && rm -f release.zip
    cd dist && 7z a release.zip fangen.exe config.toml dictionary.json


