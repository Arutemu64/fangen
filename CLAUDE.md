# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`fangen` is a Cosplay2 → Excel parser. It pulls request data from the
Cosplay2 API into a local SQLite database and exports it to Excel
workbooks. The CLI is built with [Typer](https://typer.tiangolo.com/) and
exposed as the `fangen` command (`src/fangen/__main__.py`).

## Language conventions

- **Code comments must be written in English.** This includes `#` inline
  comments and any explanatory notes in the source.
- **User-facing text must be written in Russian.** This includes CLI help
  strings, `print()` / console output, error messages, and any other text an
  end user sees while running the tool.

The audience for the two is different: contributors read the comments, and
the tool's users are Russian-speaking.

## Tooling

- Use `uv` for everything: `uv run <cmd>`, `uv sync`, etc.
- Lint: `uv run ruff check`
- Type-check: `uv run ty check`
- Target Python version is 3.14 (see `.python-version` / `pyproject.toml`).

Run `ruff check` and `ty check` before committing.

### adaptix and runtime annotations

adaptix builds its loaders by reading dataclass annotations at runtime (via
`get_type_hints`). Any type used in the annotations of an adaptix-loaded
`@dataclass` must therefore be importable at runtime — **never** hide such an
import behind `if TYPE_CHECKING:`, or config/model loading raises `NameError`.
Ruff enforces this: `runtime-evaluated-decorators = ["dataclasses.dataclass"]`
in `ruff.toml` makes the `TC` rules treat dataclass annotations as runtime
usage.

## Documentation

- **Keep `README.md` in sync with the code.** Whenever you change the CLI
  (commands, arguments, options), the config schema (`Config` /
  `config.dist.toml`), or user-facing behavior, update the matching section
  of the README in the same change. The README's usage guide is written in
  Russian (see the language conventions above); keep it that way.
