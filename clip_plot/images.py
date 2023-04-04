# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_images.ipynb.

# %% auto 0
__all__ = ['PILLoadTruncated', 'FLOATX', 'load_image', 'image_to_array', 'array_to_image', 'save_image', 'write_images',
           'get_image_paths', 'Image']

# %% ../nbs/03_images.ipynb 3
import io
import os
import glob2
import random
from copy import deepcopy
from typing import Optional, List, Union

import numpy as np
from iiif_downloader import Manifest
from PIL import Image as pil_image, ImageFile

from .utils import clean_filename, timestamp, FILE_NAME


# handle truncated images in PIL (managed by Pillow)
PILLoadTruncated  = ImageFile.LOAD_TRUNCATED_IMAGES

# %% ../nbs/03_images.ipynb 6
# Helper functions taken from Keras library

# The type of float to use throughout a session.
FLOATX = "float32"

def load_image(path: str) -> pil_image.Image:
    with open(path, "rb") as f:
        img = pil_image.open(io.BytesIO(f.read()))

    if img.mode != "RGB":
        img = img.convert("RGB")

    return img


def image_to_array(img: pil_image.Image) -> np.array:
    """Converts a PIL Image instance to a Numpy array.

    Args:
        img: Input PIL Image instance.

    Returns:
        A 3D Numpy array.

    Raises:
        ValueError: if invalid `img` or `data_format` is passed.
    """

    # Numpy array x has format (height, width, channel)
    # or (channel, height, width)
    # but original PIL image has format (width, height, channel)
    x = np.asarray(img, dtype=FLOATX)
    if len(x.shape) not in [2, 3]:
        raise ValueError(f"Unsupported image shape: {x.shape}")

    if len(x.shape) == 2:
        x = x.reshape((x.shape[0], x.shape[1], 1))
        
    return x


def array_to_image(x: np.array)-> pil_image.Image:
    """Converts a 3D Numpy array to a PIL Image instance.

    Args:
        x: Input data, in any form that can be converted to a Numpy array.

    Returns:
        A PIL Image instance.

    Raises:
        ValueError: if invalid `x` or `data_format` is passed.
    """
    x = np.asarray(x, dtype=FLOATX)
    if x.ndim != 3:
        raise ValueError(
            "Expected image array to have rank 3 (single image). "
            f"Got array with shape: {x.shape}"
        )

    # Original Numpy array x has format (height, width, channel)
    # or (channel, height, width)
    # but target PIL image has format (width, height, channel)

    x = x - np.min(x)
    x_max = np.max(x)
    if x_max != 0:
        x /= x_max
    x *= 255

    if x.shape[2] == 4:  # RGBA
        return pil_image.fromarray(x.astype("uint8"), "RGBA")
    elif x.shape[2] == 3:  # RGB
        return pil_image.fromarray(x.astype("uint8"), "RGB")
    elif x.shape[2] == 1:  # grayscale
        if np.max(x) > 255:
            # 32-bit signed integer grayscale image. PIL mode "I"
            return pil_image.fromarray(x[:, :, 0].astype("int32"), "I")
        return pil_image.fromarray(x[:, :, 0].astype("uint8"), "L")
    else:
        raise ValueError(f"Unsupported channel number: {x.shape[2]}")


def save_image(path: str, x: np.array) -> None:
    """Saves an image stored as a Numpy array to a path or file object.

    Args:
        path: Path or file object.
        x: Numpy array.
    """
    img = array_to_image(x)
    img.save(path,format=None)

# %% ../nbs/03_images.ipynb 7
def write_images(**kwargs):
    """Write all originals and thumbs to the output dir"""
    for i in Image.stream_images(image_paths=kwargs["image_paths"], metadata=kwargs["metadata"]):
        filename = clean_filename(i.path)
        # copy original for lightbox
        out_dir = os.path.join(kwargs["out_dir"], "originals")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_path = os.path.join(out_dir, filename)
        if not os.path.exists(out_path):
            resized = i.resize_to_height(600)
            resized = array_to_image(resized)
            save_image(out_path, resized)
        # copy thumb for lod texture
        out_dir = os.path.join(kwargs["out_dir"], "thumbs")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_path = os.path.join(out_dir, filename)
        img = array_to_image(i.resize_to_max(kwargs["lod_cell_height"]))
        save_image(out_path, img)

# %% ../nbs/03_images.ipynb 8
def get_image_paths(images:str, out_dir: str) -> List[str]:
    """Called once to provide a list of image paths--handles IIIF manifest input.
    
    args:
        images (str): directory location of images.
        out_dir (str): output directory for downloaded IIIF files.

    returns:
        image_paths list(str): list of image paths.

    Note:
        Old/previous images are not deleted from IIIF directory.

    Todo:
        Consider separate function that handles IIIF images
        from glob images.
    """

    image_paths = None

    # Is images a iiif file or image directory?
    if os.path.isfile(images):
        # Handle list of IIIF image inputs
        iiif_dir = os.path.join(out_dir,"iiif-downloads")

        # Check if directory already contains anything
        if os.path.exists(iiif_dir) and os.listdir(iiif_dir):
            print("Warning: IIIF directory already contains content!")

        with open(images) as f:
            urls = [url.strip() for url in f.read().split("\n") if url.startswith("http")]
            count = 0
            for url in urls:
                try:
                    Manifest(url=url, out_dir=iiif_dir).save_images(limit=1)
                    count += 1
                except:
                    print(timestamp(), "Could not download url " + url)

            if count == 0:
                raise Exception('No IIIF images were successfully downloaded!')

            image_paths = glob2.glob(os.path.join(out_dir,"iiif-downloads", "images", "*"))
   
    # handle case where images flag points to a glob of images
    if not image_paths:
        image_paths = glob2.glob(images)

    # handle case user provided no images
    if not image_paths:
        raise FileNotFoundError("Error: No input images were found. Please check your --images glob")

    return image_paths

# %% ../nbs/03_images.ipynb 10
class Image:
    def __init__(self, *args, **kwargs):
        self.path = args[0]
        self.filename = clean_filename(self.path)
        self.original = load_image(self.path) 
        self.metadata = kwargs["metadata"] if kwargs["metadata"] else {}

    def resize_to_max(self, n: int) -> np.array:
        """Resize self.original so its longest side has n pixels (maintain proportion).

        Args:
            n (int): maximum pixel length

        Returns:
            np.array: re-sized to n length
        """
        w, h = self.original.size
        if w > h:
            size = (n, int(n * h / w))
        else:
            size = (int(n * w / h), n)
    
        return image_to_array(self.original.resize(size))

    def resize_to_height(self, height: int) -> np.array:
        """Resize self.original into an image with height h and proportional width.

        Args:
            height (int): New height to resize to

        Returns:
            np.array: re-sized to height
        """
        w, h = self.original.size
        if (w / h * height) < 1:
            resizedwidth = 1
        else:
            resizedwidth = int(w / h * height)
        size = (resizedwidth, height)
        return image_to_array(self.original.resize(size))

    def resize_to_square(self, n: int, center: Optional[bool] = False) -> np.array:
        """Resize self.original to an image with nxn pixels (maintain proportion)
        if center, center the colored pixels in the square, else left align.

        Args:
            n (int)

        Notes:
            Function not being used
        """
        a = self.resize_to_max(n)
        h, w, c = a.shape
        pad_lr = int((n - w) / 2)  # left right pad
        pad_tb = int((n - h) / 2)  # top bottom pad
        b = np.zeros((n, n, 3))
        if center:
            b[pad_tb : pad_tb + h, pad_lr : pad_lr + w, :] = a
        else:
            b[:h, :w, :] = a
        return b

    def valid(self, lod_cell_height: int, oblong_ratio: Union[int,float]) -> tuple[bool, str]:
        """Validate that image can be opened and loaded correctly.

        Args:
            lod_cell_height (int):
            oblong_ratio (int|float): atlas_size/cell_size ratio

        Returns:
            Tuple[pass,msg]:
                pass (bool): True if passed validation
                msg (str): Reason why validation failed 
        """
        w, h = self.original.size
        # remove images with 0 height or width when resized to lod height
        if (h == 0) or (w == 0):
            return False, f"Skipping {self.path} because it contains 0 height or width"
        # remove images that have 0 height or width when resized
        try:
            resized = self.resize_to_max(lod_cell_height)
        except ValueError:
            return False, f"Skipping {self.path} because it contains 0 height or width when resized"
        except OSError:
            return False, f"Skipping {self.path} because it could not be resized"
        # remove images that are too wide for the atlas
        if (w / h) > (oblong_ratio):
            return False, f"Skipping {self.path} because its dimensions are oblong"

        return True, ""

    @staticmethod
    def stream_images(image_paths: List[str], metadata: Optional[List[dict]] = None) -> 'Image':
        """Read in all images from args[0], a list of image paths
        
        Args:
            image_paths (list[str]): list of image locations
            metadata (Optional[list[dist]]): metadata for each image
        
        Returns:
            yields Image instance

        Notes:
            image is matched to metadata by index location
                Matching by key would be better
        """
        for idx, imgPath in enumerate(image_paths):
            try:
                meta = None
                if metadata and metadata[idx]:
                    meta = metadata[idx]
                yield Image(imgPath, metadata=meta)
            except Exception as exc:
                print(timestamp(), "Image", imgPath, "could not be processed --", exc)
