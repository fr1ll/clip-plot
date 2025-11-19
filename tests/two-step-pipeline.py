"""
test two-step pipeline:
1. embed images and save table
2. create plot from table
"""

from shutil import rmtree
from pathlib import Path
from pprint import pprint

from clip_plot.pipelines import embed_images_pipeline, project_images_pipeline
from clip_plot.configuration import Cfg

libroot = Path(__file__).parents[1]
print(f"libroot: {libroot.resolve()}")
OUTPUT_DIR: Path = libroot / "tests/smithsonian_butterflies_10/two-step-test/"
LOCAL_MODEL: Path = libroot / "models/timm__vit_pe_core_tiny_patch16_384.fb"
IMAGE_GLOB: str = (libroot / "datasets/smithsonian_butterflies_150sm/jpgs/*.jpg").as_posix()
META_GLOB: str = (libroot / "datasets/smithsonian_butterflies_150sm/2023-12-21_butterflies-150sm-meta.csv").as_posix()
TABLE_ID: str = "woofy"

if OUTPUT_DIR.exists():
  rmtree(OUTPUT_DIR)

###----global vars for config for Step 2:

TAGLINE: str = "Smithsonian Butterflies - Two Step Pipeline Test"
ATLAS_ROW_HEIGHT: int = 64
N_NEIGHBORS: int = 15
MIN_DIST: float = 0.1
MIN_CLUSTER_SIZE: int = 2

cfg_step1 = Cfg(paths={"images": IMAGE_GLOB,
                            "metadata": META_GLOB,
                            "output_dir": OUTPUT_DIR,
                            "table_id": TABLE_ID,
                                 },
                           model=LOCAL_MODEL.as_posix(),
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
                     view_opts={"tagline": TAGLINE},
                     image_opts={"atlas_row_height": ATLAS_ROW_HEIGHT},
                     umap_spec={"n_neighbors": N_NEIGHBORS,
                                "min_dist": MIN_DIST},
                     cluster_spec={"min_cluster_size": MIN_CLUSTER_SIZE},
                    )

pprint(cfg_step1.model_dump())

project_images_pipeline(
                   output_dir=cfg_step2.paths.output_dir,
                   plot_id=cfg_step2.plot_id,
                   model=cfg_step2.model,
                   viewer_opts=cfg_step2.view_opts,
                   umap_spec=cfg_step2.umap_spec,
                   cluster_spec=cfg_step2.cluster_spec,
                   image_opts=cfg_step2.image_opts,
                   tables=cfg_step2.paths.tables,
                   )

print("=== Finished Step 2: Creating Viewer ===")
