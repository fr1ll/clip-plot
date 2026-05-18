Use `uv` for local project setup and running.

## git habits

- use `git mv` and `git rm` for file reorg
- prefer small commits

## Environment

- From the repository root, run `uv sync --all-extras` to create/update `.venv`.
- Run Python and project tools through `uv run`, for example `uv run python`.
- This nbdev install exposes hyphenated console scripts. Use `uv run nbdev-prepare`; `uv run nbdev prepare`, `uv run nbdev`, and `uv run nbdev_prepare` are not valid here.
- Hugging Face is configured through `.env` and loaded on folder entry by `.envrc`/direnv. If direnv has not loaded it yet, run `direnv allow` from the repository root.

## nbdev Prepare

To start the full nbdev preparation workflow:

```bash
uv sync --all-extras
uv run nbdev-prepare
```

As of this note, `nbdev-prepare` starts but fails during notebook tests:

- `nbs/08_from_tables.ipynb`: Polars DataFrame equality assertion differs by column order (`a, c, b` vs `a, b, c`).
- `nbs/13_pipelines.ipynb`: `test_butterfly()` raises `ValueError: No images found from either tables or images input.`

## Python Style

Preferred modern, functional Python:

- dataclasses over handwritten classes
- `pathlib.Path` for path manipulation
- small functions when possible
- use the walrus operator when it helps
- pipeline pattern when possible
- pydantic for validation