# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_metadata.ipynb.

# %% auto 0
__all__ = ['get_metadata_list', 'write_metadata', 'get_manifest']

# %% ../nbs/07_metadata.ipynb 3
import os
import csv
import json
from glob import glob
from math import ceil
from datetime import datetime
from collections import defaultdict
from typing import Optional, List, Union

import numpy as np

from .utils import clean_filename, FILE_NAME
from .layouts import get_layouts, get_heightmap, get_hotspots
from .utils import is_number, get_path, get_version, write_json, read_json

# %% ../nbs/07_metadata.ipynb 5
def get_metadata_list(meta_dir: str) -> Union[List[dict], List[str]]:
    """Return a list of objects with image metadata.

    Will create 'tags' key if 'category' is in metadata
    but not 'tags'.
    
    Args:
        metadata (str, default = None): Metadata location

    Returns:
        l (List[dict]): List of metadata 

    Notes:
        No check for 'filename' is performed

    Todo:
        Think about separating .csv and json functionality.
        Can we use pandas numpy to process csv?
    """

    # handle csv metadata
    metaList = []
    if meta_dir.endswith(".csv"):
        with open(meta_dir) as f:
            reader = csv.reader(f)
            headers = [i.lower() for i in next(reader)]
            for i in reader:
                metaList.append(
                    {
                        headers[j]: i[j] if len(i) > j and i[j] else ""
                        for j, _ in enumerate(headers)
                    }
                )
    
    # handle json metadata
    else:
        for i in glob(meta_dir, recursive=True):
            with open(i) as f:
                metaList.append(json.load(f))

    # if the user provided a category but not a tag, use the category as the tag
    for metaDict in metaList:
        if "category" in metaDict and ("tags" in metaDict) is False:
            metaDict.update({"tags": metaDict["category"]})
    return metaList, headers

# %% ../nbs/07_metadata.ipynb 6
def write_metadata(imageEngine, gzip: Optional[bool] = False, encoding:  Optional[str] = 'utf8'):
    """Write list `metadata` of objects to disk
    
    Args:
        metadata (list[dict])
        out_dir (str)

        subfunctions:
            write_json():
                gzip (Optional[bool]):
                encoding (Optional[str]): Required if gzip is provided
                    default = 'utf8'

    Returns:
        None

    Notes:
        Improve variable naming
    
    """
    metadata = imageEngine.metadata
    out_dir = imageEngine.out_dir

    if not metadata:
        return
    
    # Create kwargs replacement for write_json function
    writeJasonDict = {'encoding': encoding, 'gzip': gzip}

    out_dir = os.path.join(out_dir, "metadata")
    for i in ["filters", "options", "file"]:
        out_path = os.path.join(out_dir, i)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
    
    # Create the lists of images with each tag
    d = defaultdict(list)
    for img in imageEngine:
        i = img.metadata
        filename = img.unique_name
        i["tags"] = [j.strip() for j in i.get("tags", "").split("|")]
        for j in i["tags"]:
            d["__".join(j.split())].append(filename)
        write_json(os.path.join(out_dir, "file", filename + ".json"), i, **writeJasonDict)

    write_json(
        os.path.join(out_dir, "filters", "filters.json"),
        [
            {
                "filter_name": "select",
                "filter_values": list(d.keys()),
            }
        ],
        **writeJasonDict
    )

    # create the options for the category dropdown
    for i in d:
        write_json(os.path.join(out_dir, "options", i + ".json"), d[i], **writeJasonDict)
    
    # create the map from date to images with that date (if dates present)
    date_d = defaultdict(list)
    for i in metadata:
        date = i.get("year", "")
        if date:
            date_d[date].append(clean_filename(i[FILE_NAME]))

    # find the min and max dates to show on the date slider
    dates = np.array([int(i.strip()) for i in date_d if is_number(i)])
    domain = {"min": float("inf"), "max": -float("inf")}
    mean = np.mean(dates)
    std = np.std(dates)
    for i in dates:
        # update the date domain with all non-outlier dates
        if abs(mean - i) < (std * 4):
            domain["min"] = int(min(i, domain["min"]))
            domain["max"] = int(max(i, domain["max"]))

    # write the dates json
    if len(date_d) > 1:
        write_json(
            os.path.join(out_dir, "dates.json"),
            {
                "domain": domain,
                "dates": date_d,
            },
            **writeJasonDict
        )

# %% ../nbs/07_metadata.ipynb 7
##
# Main
##


def get_manifest(imageEngine, **kwargs):
    """Create and return the base object for the manifest output file
    
    Args:
        atlas_dir (str)
        image_paths (str)
        plot_id (str, default = str(uuid.uuid1()))
        out_dir (str)
        metadata (list[dict]): Only checking if provided
        gzip (bool, default = False)
        atlas_size (int, default = 2048)
        cell_size (int, default = 32)
        lod_cell_height (int, default = 128)

        Need to check subfunctions


    Returns:
        None

    Notes:
        Original description is inadequate
        Function is to big (god function)
    
    """
    # load the atlas data
    atlas_data = json.load(open(os.path.join(kwargs["atlas_dir"], "atlas_positions.json")))
    # store each cell's size and atlas position
    atlas_ids = set([i["idx"] for i in atlas_data])
    sizes = [[] for _ in atlas_ids]
    pos = [[] for _ in atlas_ids]
    for idx, i in enumerate(atlas_data):
        sizes[i["idx"]].append([i["w"], i["h"]])
        pos[i["idx"]].append([i["x"], i["y"]])

    # obtain the paths to each layout's JSON positions
    layouts = get_layouts(imageEngine, **kwargs)
    # create a heightmap for the umap layout
    if "umap" in layouts and layouts["umap"]:
        get_heightmap(layouts["umap"]["variants"][0]["layout"], "umap", **kwargs)
    
    # specify point size scalars
    point_sizes = {}
    point_sizes["min"] = 0
    point_sizes["grid"] = 1 / ceil(imageEngine.count ** (1 / 2))
    point_sizes["max"] = point_sizes["grid"] * 1.2
    point_sizes["scatter"] = point_sizes["grid"] * 0.2
    point_sizes["initial"] = point_sizes["scatter"]
    point_sizes["categorical"] = point_sizes["grid"] * 0.6
    point_sizes["geographic"] = point_sizes["grid"] * 0.025

    # fetch the date distribution data for point sizing
    if "date" in layouts and layouts["date"]:
        date_layout = read_json(layouts["date"]["labels"], **kwargs)
        point_sizes["date"] = 1 / (
            (date_layout["cols"] + 1) * len(date_layout["labels"])
        )

    # create manifest json
    manifest = {
        "version": get_version(),
        "plot_id": kwargs["plot_id"],
        "output_directory": os.path.split(kwargs["out_dir"])[0],
        "layouts": layouts,
        "initial_layout": "umap",
        "point_sizes": point_sizes,
        "imagelist": get_path("imagelists", "imagelist", **kwargs),
        "atlas_dir": kwargs["atlas_dir"],
        "metadata": True if imageEngine.metadata else False,
        "default_hotspots": get_hotspots(imageEngine, layouts=layouts,
                                         n_preproc_dims=kwargs["cluster_preproc_dims"],
                                         **kwargs),
        "custom_hotspots": get_path(
            "hotspots", "user_hotspots", add_hash=False, **kwargs
        ),
        "gzipped": kwargs["gzip"],
        "config": {
            "sizes": {
                "atlas": imageEngine.atlas_size,
                "cell": imageEngine.cell_size,
                "lod": imageEngine.lod_cell_height,
            },
        },
        "creation_date": datetime.today().strftime("%d-%B-%Y-%H:%M:%S"),
    }

    # store parameters that will impact embedding
    embed_params = ["embed_model", "n_neighbors", "min_dist", "metric", "max_clusters", "min_cluster_size"]
    for e in embed_params:
        manifest.update({e: kwargs[e]})

    # write the manifest without gzipping
    no_gzip_kwargs = {
        "out_dir": kwargs["out_dir"],
        "gzip": False,
        "plot_id": kwargs["plot_id"],
    }
    path = get_path("manifests", "manifest", **no_gzip_kwargs)
    write_json(path, manifest, **no_gzip_kwargs)
    path = get_path(None, "manifest", add_hash=False, **no_gzip_kwargs)
    write_json(path, manifest, **no_gzip_kwargs)

    # create images json
    imagelist = {
        "cell_sizes": sizes,
        "images": [img.unique_name for img in imageEngine],
        "atlas": {
            "count": len(atlas_ids),
            "positions": pos,
        },
    }
    write_json(manifest["imagelist"], imagelist, **kwargs)
