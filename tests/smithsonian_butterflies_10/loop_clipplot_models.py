from clip_plot.clip_plot import project_images
from pathlib import Path
import time
from glob import glob

EMBED_MODELS = [
    "timm/vit_large_patch16_dinov3.sat493m",
    "timm/convnext_tiny.dinov3_lvd1689m",
    "timm/vit_small_patch16_dinov3.lvd1689m",
    "timm/vit_large_patch16_dinov3.lvd1689m",
    "timm/vit_large_patch16_dinov3.sat493m",
    "timm/ViT-SO400M-14-SigLIP2-378",
    "timm/PE-Core-L-14-336"
]

JPGS = "jpgs/*"

def quick_check_images(jpgs: str):
    print(f"First five images: {list(Path().glob(jpgs))[:5]}")

def ck_img_v2(jpgs: str):
    image_paths = glob(jpgs, recursive=True)
    print(f"First five, second way: {image_paths[:5]}")

def clipplot_many_models(embed_models: list, jpgs: str):
    """
    loop through some embedding models
    and create clipplot viewers for each
    """
    quick_check_images(jpgs)
    ck_img_v2(jpgs)
    # image_paths = glob(jpgs, recursive=True)
    for m in embed_models:
        start = time.time()
        print(f"Starting with embedding model {m} at {start}")
        project_images.__wrapped__(images=jpgs,
                       out_dir=f"test_outs/{m.split('/')[-1]}",
                       embed_model=m
                       )
        end = time.time()
        print(f"Ending time: {end}\tElapsed time: {end-start}")


if __name__ == "__main__":
    clipplot_many_models(embed_models=EMBED_MODELS, jpgs=JPGS)
    
