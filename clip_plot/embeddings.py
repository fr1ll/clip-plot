# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_embeddings.ipynb.

# %% auto 0
__all__ = ['get_inception_vectors']

# %% ../nbs/04_embeddings.ipynb 3
from .utils import timestamp, clean_filename
from .images import image_to_array, Image

from pathlib import Path

### Graveyard of attempts to silence tensorflow
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import tensorflow as tf
tf.compat.v1.logging.set_verbosity(40) # ERROR

from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.models import Model
from tensorflow.keras.applications.inception_v3 import preprocess_input

from tqdm.auto import tqdm
import numpy as np

# %% ../nbs/04_embeddings.ipynb 5
def get_inception_vectors(imageEngine,**kwargs):
    """Create and return Inception vector representation of Image() instances"""

    vector_dir = Path(kwargs["out_dir"]) / "image-vectors" / "inception"
    vector_dir.mkdir(exist_ok=True, parents=True)
    base = InceptionV3(
        include_top=True,
        weights="imagenet",
    )
    model = Model(inputs=base.input, outputs=base.get_layer("avg_pool").output)
    tf.random.set_seed(kwargs["seed"])

    print(timestamp(), "Creating Inception vectors")
    vecs = []   

    for img in tqdm(imageEngine, total=len(imageEngine.image_paths)):
        vector_path = vector_dir / (img.filename + ".npy")
        if vector_path.exists() and kwargs["use_cache"]:
            vec = np.load(vector_path)
        else:
            img_processed = preprocess_input(image_to_array(img.original.resize((299, 299))))
            vec = model.predict(np.expand_dims(img_processed, 0), verbose = 0).squeeze()
            np.save(vector_path, vec)
        vecs.append(vec)
    return np.array(vecs)
