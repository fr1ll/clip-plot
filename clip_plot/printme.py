from pathlib import Path

print(Path(__file__).parent.as_posix())

print(__file__)

globals()['_dh'][0].as_posix()