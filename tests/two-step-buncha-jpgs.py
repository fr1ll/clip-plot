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
OUTPUT_DIR: Path = libroot / "tests/1200-imgs/two-step-test/"
IMAGE_GLOB: str = (libroot / "datasets/StreetView-Image-Dataset-10K_Limit1200/*.jpg").as_posix()
META_GLOB: str = (libroot / "datasets/StreetView-Image-Dataset-10K_Limit1200/Sadhana-24__StreetView-Image-Dataset-10K__1200_meta.parquet/*.parquet").as_posix()
TABLE_ID: str = "null"

# local model if it exists
MODEL = (libroot / "models/timm__vit_pe_core_tiny_patch16_384.fb").as_posix()
if not Path(MODEL).exists():
    MODEL = "timm/vit_pe_core_tiny_patch16_384.fb"

if OUTPUT_DIR.exists():
  rmtree(OUTPUT_DIR)

###----global vars for config for Step 2:

TAGLINE: str = "Smithsonian Butterflies - Two-step Pipeline Test"
N_NEIGHBORS: int = 30
MIN_DIST: float = 0.01
MIN_CLUSTER_SIZE: int = 5

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
                     view_opts={"tagline": TAGLINE},
                     umap_spec={"n_neighbors": N_NEIGHBORS,
                                "min_dist": MIN_DIST},
                     cluster_spec={"min_cluster_size": MIN_CLUSTER_SIZE},
                     image_path_col="local_path",
                     x_col="long",
                     y_col="lat",
                    )

# pprint(cfg_step1.model_dump())

project_images_pipeline(
                   output_dir=cfg_step2.paths.output_dir,
                   plot_id=cfg_step2.plot_id,
                   model=cfg_step2.model,
                   viewer_opts=cfg_step2.view_opts,
                   umap_spec=cfg_step2.umap_spec,
                   cluster_spec=cfg_step2.cluster_spec,
                   image_opts=cfg_step2.image_opts,
                   tables=cfg_step2.paths.tables,
                   image_path_col=cfg_step2.image_path_col,
                   x_col=cfg_step2.x_col,
                   y_col=cfg_step2.y_col,
                   )

print("=== Finished Step 2: Creating Viewer ===")
