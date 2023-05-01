# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_images.ipynb.

# %% auto 0
__all__ = ['PILLoadTruncated', 'FLOATX', 'load_image', 'image_to_array', 'array_to_image', 'save_image', 'write_images',
           'get_image_paths', 'create_atlas_files', 'save_atlas', 'Image', 'ImageFactory']

# %% ../nbs/03_images.ipynb 3
import io
import os
import json
import glob2
from typing import Optional, List, Union

import numpy as np
from iiif_downloader import Manifest
from PIL import Image as pil_image, ImageFile
from tqdm.auto import tqdm

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
def write_images(image_paths: List[str], metadata: List[dict],
                 out_dir: str, lod_cell_height: int) -> None:
    """Write all originals and thumbnails images to the output dir.

    Images are used by lightbox.
    
    Args:
        image_paths (List[str]): List of path of images
        metadata (List[dict]): List of dictionaries with image metadata
        out_dir (str): Output Directory
        lod_cell_height (int): Cell height for lod texture

    Returns:
        None

    Notes:
        - Will only output the original image to the out dir if 
          there is no existing image with the exact same name.
        - Thumbnails are always saved regardless if a file 
          already exists.

    TODO:
        Should users get a warning that a photo already exists
        in the destination folder?
    """
    for img in Image.stream_images(image_paths=image_paths, metadata=metadata):
        filename = clean_filename(img.path)
        # Copy original for lightbox
        org_out_dir = os.path.join(out_dir, "originals")
        if not os.path.exists(org_out_dir):
            # Create directory since it does not exists
            os.makedirs(org_out_dir)
        out_path = os.path.join(org_out_dir, filename)

        # Does the image already exist?
        if not os.path.exists(out_path):
            resized = img.resize_to_height(600)
            resized = array_to_image(resized)
            save_image(out_path, resized)
    
        # copy thumb for lod texture
        thu_out_dir = os.path.join(out_dir, "thumbs")
        if not os.path.exists(thu_out_dir):
            os.makedirs(thu_out_dir)
            
        out_path = os.path.join(thu_out_dir, filename)
        resized_max = array_to_image(img.resize_to_max(lod_cell_height))
        save_image(out_path, resized_max)

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
##
# Atlases
##


def create_atlas_files(imageEngine,**kwargs):
    """
    Generate and save to disk all atlases to be used for this visualization
    If square, center each cell in an nxn square, else use uniform height

    Args:
        out_dir (str)
        plot_id (str, default = str(uuid.uuid1()))
        use_cache (bool, default = False)
        shuffle (Optional[bool], default = False)
        atlas_size (int, default = 2048)
        cell_size (int, default = 32)
        lod_cell_height (int, default = 128)


    Returns:
        out_dir (str): Atlas location 

    Notes:

    """
    # if the atlas files already exist, load from cache
    out_dir = os.path.join(kwargs["out_dir"], "atlases", kwargs["plot_id"])
    if (
        os.path.exists(out_dir)
        and kwargs["use_cache"]
        and not kwargs.get("shuffle", False)
    ):
        print(timestamp(), "Loading saved atlas data")
        return out_dir
    
    # Else create the atlas images and store the positions of cells in atlases
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    print(timestamp(), "Creating atlas files")
    n = 0  # number of atlases
    x = 0  # x pos in atlas
    y = 0  # y pos in atlas
    positions = []  # l[cell_idx] = atlas data
    atlas = np.zeros((imageEngine.atlas_size, imageEngine.atlas_size, 3))

    for img in tqdm(imageEngine,total=imageEngine.count):
        
        cell_data = img.resize_to_height(imageEngine.cell_size)
        _, v, _ = cell_data.shape
        appendable = False
        if (x + v) <= imageEngine.atlas_size:
            appendable = True
        elif (y + (2 * imageEngine.cell_size)) <= imageEngine.atlas_size:
            y += imageEngine.cell_size
            x = 0
            appendable = True
        if not appendable:
            save_atlas(atlas, out_dir, n)
            n += 1
            atlas = np.zeros((imageEngine.atlas_size, imageEngine.cell_size, 3))
            x = 0
            y = 0
        atlas[y : y + imageEngine.cell_size, x : x + v] = cell_data
        # find the size of the cell in the lod canvas
        lod_data = img.resize_to_max(imageEngine.lod_cell_height)
        h, w, _ = lod_data.shape  # h,w,colors in lod-cell sized image `i`
        positions.append(
            {
                "idx": n,  # atlas idx
                "x": x,  # x offset of cell in atlas
                "y": y,  # y offset of cell in atlas
                "w": w,  # w of cell at lod size
                "h": h,  # h of cell at lod size
            }
        )
        x += v
    save_atlas(atlas, out_dir, n)
    out_path = os.path.join(out_dir, "atlas_positions.json")
    with open(out_path, "w") as out:
        json.dump(positions, out)
    return out_dir


def save_atlas(atlas: np.array, out_dir: str, n: int) -> None:
    """Save an atlas to disk
    
    Args:
        atlas (np.array): Atlas
        out_dir (str): Atlas output directory
        n (int): Atlas subindex
    """
    out_path = os.path.join(out_dir, "atlas-{}.jpg".format(n))
    save_image(out_path, atlas)

# %% ../nbs/03_images.ipynb 12
class Image:
    def __init__(self, img_path: str, metadata: Optional[dict] = None) -> 'Image':
        self.path = img_path
        self._original = None
        self.metadata = metadata if metadata else {}

    @property
    def filename(self):
        return clean_filename(self.path)

    @property
    def original(self):
        if self._original is None:
            self._original = load_image(self.path) 

        return self._original

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
                yield Image(imgPath, meta)
            except Exception as exc:
                print(timestamp(), "Image", imgPath, "could not be processed --", exc)

            
import random
import copy
from .metadata import get_metadata_list

class ImageFactory():
    _OPTIONS = {
        'shuffle': False, # (Optional[bool], default = False): Shuffle image order
        'seed': "", # (int): Seed for random generator
        'max_images': False, # (Union[False,int]): Maximum number of images
        'atlas_size': 2048, # (int, default = 2048)
        'cell_size': 32, # (int, default = 32)
        'lod_cell_height': 128, # (int, default = 128)
        'validate': True, # Validate Images
    }
    
    def __init__(self, img_path, out_dir, meta_dir, options={}) -> None:
        self.img_path = img_path
        self.meta_dir = meta_dir
        self.out_dir = out_dir
        self.filenames = []
        
        for option, default in self._OPTIONS.items():
            setattr(self, option, options.get(option, default))

        self.filter_images()

    def __iter__(self):
        for img in Image.stream_images(image_paths=self.image_paths, metadata=self.metadata):
            yield img


    def filter_images(self):
        """Main method for filtering images given user metadata (if provided)

        -Validate image:
            Loading (done by stream_images and Images)
            Size
            resizing
            oblong

        -Compare against metadata

        
        Args:
            images (str): Directory location of images.
            out_dir (str): Output directory.
            shuffle (Optional[bool], default = False): Shuffle image order
            seed (int): Seed for random generator
            max_images (Union[bool,int]): Maximum number of images
            atlas_size (int, default = 2048)
            cell_size (int, default = 32)
            lod_cell_height (int, default = 128)
            meta_dir (str): Directory of image metadata

        Returns:
            images (list[str])
            metadata (list[dict])

        Notes:
            Assumes 'filename' is provided in metadata
            Convoluted compiling of metadata
            Should All Validation should belong to Image class?
            Need to split function
        """
        # validate that input image names are unique
        image_paths = get_image_paths(images=self.img_path, out_dir=self.out_dir)
        image_names = list(map(clean_filename,image_paths))
        duplicates = set([x for x in image_names if image_names.count(x) > 1])

        if duplicates:
            raise Exception(
                """Image filenames should be unique, but the following 
                filenames are duplicated\n{}""".format("\n".join(duplicates)))
        
        # optionally shuffle the image_paths
        if self.shuffle:
            print(timestamp(), "Shuffling input images")
            random.Random(self.seed).shuffle(image_paths)
        else:
            image_paths = sorted(image_paths)

        # Optionally limit the number of images in image_paths
        if self.max_images:
            image_paths = image_paths[: self.max_images]        

        # process and filter the images
        filtered_image_paths = {}
        oblong_ratio = self.atlas_size/ self.cell_size

        print(timestamp(), "Validating input images")
        for img in tqdm(Image.stream_images(image_paths=image_paths), total=len(image_paths)):
            if self.validate is True:
                valid, msg = img.valid(lod_cell_height=self.lod_cell_height, oblong_ratio=oblong_ratio) 
                if valid is True:
                    filtered_image_paths[img.path] = img.filename
                else:
                    print(timestamp(), msg)
            else:
                filtered_image_paths[img.path] = img.filename
                

        # if there are no remaining images, throw an error
        if len(filtered_image_paths) == 0:
            raise Exception("No images were found! Please check your input image glob.")

        # handle the case user provided no metadata
        if not self.meta_dir:
            self.image_paths = list(filtered_image_paths.keys())
            self.metadata = []
            self.count = len(self.image_paths)
            self.filenames = list(filtered_image_paths.values())
            return

        # handle user metadata: retain only records with image and metadata
        metaList = get_metadata_list(meta_dir=self.meta_dir)
        metaDict = {clean_filename(i.get(FILE_NAME, "")): i for i in metaList}
        meta_bn = set(metaDict.keys())
        img_bn = set(filtered_image_paths.values())

        # identify images with metadata and those without metadata
        meta_present = img_bn.intersection(meta_bn)
        meta_missing = list(img_bn - meta_bn)

        # notify the user of images that are missing metadata
        if meta_missing:
            print(
                timestamp(),
                " ! Some images are missing metadata:\n  -",
                "\n  - ".join(meta_missing[:10]),
            )
            if len(meta_missing) > 10:
                print(timestamp(), " ...", len(meta_missing) - 10, "more")

            if os.path.exists(self.out_dir) is False:
                os.makedirs(self.out_dir)
                
            missing_dir = os.path.join(self.out_dir,"missing-metadata.txt")
            with open(missing_dir, "w") as out:
                out.write("\n".join(meta_missing))

        if not meta_present:
            raise Exception( f"""No image has matching metadata. Check if '{FILE_NAME}' key was provided in metadata files""")

        # get the sorted lists of images and metadata
        images = []
        metadata = []
        for path, fileName in filtered_image_paths.items():
            if fileName in meta_present:
                images.append(path)
                metadata.append(copy.deepcopy(metaDict[fileName]))
                self.filenames.append(fileName)

        self.image_paths = images
        self.metadata = metadata
        self.count = len(self.image_paths)


    def write_images(self) -> None:
        """Write all originals and thumbnails images to the output dir.

        Images are used by lightbox.
        
        Args:
            image_paths (List[str]): List of path of images
            metadata (List[dict]): List of dictionaries with image metadata
            out_dir (str): Output Directory
            lod_cell_height (int): Cell height for lod texture

        Returns:
            None

        Notes:
            - Will only output the original image to the out dir if 
            there is no existing image with the exact same name.
            - Thumbnails are always saved regardless if a file 
            already exists.

        TODO:
            Should users get a warning that a photo already exists
            in the destination folder?
        """
        org_out_dir = os.path.join(self.out_dir, *["data", "originals"])
        if not os.path.exists(org_out_dir):
            # Create directory since it does not exists
            os.makedirs(org_out_dir)

        thu_out_dir = os.path.join(self.out_dir, *["data", "thumbs"])
        if not os.path.exists(thu_out_dir):
            os.makedirs(thu_out_dir)

        print(timestamp(), "Writing Originals and thumbnail images")
        for img in tqdm(self, total=self.count):
            filename = img.filename
            # Copy original for lightbox
            out_path = os.path.join(org_out_dir, filename)

            # Does the image already exist?
            if not os.path.exists(out_path):
                resized = img.resize_to_height(600)
                resized = array_to_image(resized)
                save_image(out_path, resized)
        
            # copy thumb for lod texture
            out_path = os.path.join(thu_out_dir, filename)
            resized_max = array_to_image(img.resize_to_max(self.lod_cell_height))
            save_image(out_path, resized_max)
