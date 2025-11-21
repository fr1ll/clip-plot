"""
test two-step pipeline:
1. embed images and save table
2. create plot from table
"""

from pathlib import Path
from shutil import rmtree

from clip_plot.configuration import Cfg
from clip_plot.pipelines import embed_images_pipeline, tables_to_emb_atlas

libroot = Path(__file__).parents[1]
print(f"libroot: {libroot.resolve()}")
OUTPUT_DIR: Path = libroot / "tests/smithsonian_butterflies_10/two-step-to-atlas/"
IMAGE_GLOB: str = (libroot / "datasets/smithsonian_butterflies_150sm/jpgs/*.jpg").as_posix()
META_GLOB: str = (libroot / "datasets/smithsonian_butterflies_150sm/2023-12-21_butterflies-150sm-meta.csv").as_posix()
TABLE_ID: str = "inp-to-atlas"

# local model if it exists
MODEL = (libroot / "models/timm__vit_pe_core_tiny_patch16_384.fb").as_posix()
if not Path(MODEL).exists():
    print("Using remote model")
    MODEL = "timm/vit_pe_core_tiny_patch16_384.fb"

if OUTPUT_DIR.exists():
  rmtree(OUTPUT_DIR)

###----global vars for config for Step 2:

N_NEIGHBORS: int = 15
REDUCER: str = "localmap"

cfg_step1 = Cfg(paths={"images": IMAGE_GLOB,
                            "metadata": META_GLOB,
                            "output_dir": OUTPUT_DIR,
                            "table_id": TABLE_ID,
                                 },
                           model=MODEL,
                           )

# pprint(cfg_step1.model_dump())

embed_images_pipeline(images=cfg_step1.paths.images,
                        model=cfg_step1.model,
                        metadata=cfg_step1.paths.metadata,
                        output_dir=cfg_step1.paths.output_dir,
                        table_format=cfg_step1.paths.table_format,
                        table_id=cfg_step1.paths.table_id,
                )

print("=== Finished Step 1: Embedding Images ===")

cfg_step2 = Cfg(paths={"tables":
                              OUTPUT_DIR/"data"/"tables"/"EmbedImages__*.parquet",
                            "output_dir": OUTPUT_DIR},
                     umap_spec={"n_neighbors": N_NEIGHBORS,
                                "reducer": REDUCER,
                                },
                    )

# pprint(cfg_step1.model_dump())

tables_to_emb_atlas(tables=cfg_step2.paths.tables,
                   umap_spec=cfg_step2.umap_spec,
                   output_dir=cfg_step2.paths.output_dir,
                   plot_id=cfg_step2.plot_id,
                   )

print("=== Finished Step 2: Creating Viewer ===")
