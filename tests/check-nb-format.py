import nbformat
from pathlib import Path

for f in Path("../nbs/").glob("*.ipynb"):
    try:
        nb = nbformat.read(f, as_version=4)
        nbformat.validate(nb)
        print(f"{f}: OK")
    except Exception as e:
        print(f"{f}: ERROR - {e}")
