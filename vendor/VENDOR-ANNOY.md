# Vendored wheels for `annoy`

[`annoy`](https://pypi.org/spotify/annoy) currently does not provide linux wheels.

To avoid the pain of building this package from sources, we vendor pre-built wheels for common linux platforms:

1. Clone the latest repository from GitHub
2. Set up a uv-based virtual environment
3. Do `uv build --wheel`
4. Make wheels generic for linux platforms with `auditwheel repair`
5. Copy the resulting wheels from `annoy/dist/wheelhouse/` to `clip-plot/vendor/`

We leave annoy off the dependencies table in `pyproject.toml` so users have the choice whether to install the wheels or to install via PyPI.

To use vendored wheels, add to your `pyproject.toml` when consuming clip-plot:

```toml
[dependencies]
"annoy",

...

[tool.uv.sources]
annoy = { url = "https://github.com/fr1ll/clip-plot/vendor/annoy/foldername/wheelname.whl" }
```

Replace `foldername` and `wheelname` with the actual folder and wheel file names.

Note this does imply you will need to hardcode the wheelname, which implies hardcoding the Python version.
