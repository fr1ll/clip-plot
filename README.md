# ClipPlot

## 🚧 work in progress

The goal of this repo is to use [`pix-plot`](https://github.com/YaleDHLab/pix-plot) as a front end for exploring [`clip_retrieval`](https://github.com/rom1504/clip-retrieval) embeddings.

If you want to go directly from a folder of JPGs to a clipplot visualization, you should use [`pix-plot`](https://github.com/YaleDHLab/pix-plot) itself.

This is a work-in-progress attempt to enable you to generate a PixPlot visualization after creating embeddings.

## Why do this?

1. `clip` gives useful embeddings as shown by the [first place solution](https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359316) in the recent "Google Universal Image Embeddings" Kaggle competition
2. Separating the embeddings step gives more flexibility in how it is run -- for example, it can be run in parallel on several nodes
3. Separating the embeddings step also makes it easier to remove pinned dependencies so the exciting viz stuff is easier to install

## Initial ambitions coming from clipplot:

- [x] Unpin requirements versions
- [ ] Remove all TensorFlow dependencies
- [ ] Enable to go directly from what you'd expect to have after running `clip-retrieval` inference: i.e. a folder of JPGs and a folder with embeddings in numpy format


## Later ambitions

- [ ] Add a linear dimensionality reduction method to complement UMAP
- [ ] Include option to output as a desktop app via Tauri
- [ ] BYO logo


## Acknowledgements

`clip-plot` is a fork of [`pix-plot`](https://github.com/YaleDHLab/pix-plot) by [Douglas Duhaime](https://github.com/duhaime), [Peter Leonard](https://github.com/pleonard212), and others, and mainly aims to be a lighter, smaller version of their work.

The DHLab would like to thank [Cyril Diagne](http://cyrildiagne.com/) and [Nicolas Barradeau](http://barradeau.com), lead developers of the spectacular [Google Arts Experiments TSNE viewer](https://artsexperiments.withgoogle.com/tsnemap/), for generously sharing ideas on optimization techniques used in this viewer, and [Lillianna Marie](https://github.com/lilliannamarie) for naming this viewer clipplot.
