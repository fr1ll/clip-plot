from pathlib import Path

import polars as pl

from clip_plot import to_emb_atlas


def test_create_emb_atlas_prepares_daft_inputs(tmp_path, monkeypatch):
    image_dir = Path("tests/smithsonian_butterflies_10/jpgs")
    image_paths = sorted(image_dir.glob("*.jpg"))[:3]
    assert len(image_paths) == 3

    table = pl.DataFrame(
        {
            "image_path": [path.resolve().as_posix() for path in image_paths],
            "emb_x": [0.0, 0.5, 1.0],
            "emb_y": [1.0, 0.5, 0.0],
            "category": ["a", "b", "c"],
        }
    )
    captured = {}

    def fake_run_emb_atlas(parquet_path, zip_path, viewer_dir, temp_dir):
        captured["parquet_path"] = parquet_path
        captured["zip_path"] = zip_path
        captured["viewer_dir"] = viewer_dir
        captured["temp_dir"] = temp_dir

        assert parquet_path.exists()
        prepared = pl.read_parquet(parquet_path)
        assert prepared.height == len(image_paths)
        assert "image_preview" in prepared.columns
        assert "image_local_path" in prepared.columns
        assert "image_path" in prepared.columns
        assert "image_local_abspath" in prepared.columns
        assert prepared["image_local_path"].str.starts_with("jpg_originals/").all()

    monkeypatch.setattr(to_emb_atlas, "run_emb_atlas", fake_run_emb_atlas)

    to_emb_atlas.create_emb_atlas(
        table,
        image_path_col="image_path",
        viewer_dir=tmp_path,
        plot_id="test",
        mode="RGB",
    )

    assert captured["viewer_dir"] == tmp_path
    assert captured["zip_path"].suffix == ".zip"
    assert (tmp_path / "jpg_originals").is_dir()
