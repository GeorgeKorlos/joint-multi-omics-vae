import json
import pandas as pd
from src.data.io import read_omics_clean, OMICS_PATH
from src.data.preprocess import Standardizer, select_top_genes, SELECTED_GENES_PATH

SPLIT_PATH = "data/processed/split.json"
SCALER_PATH = "data/processed/scaler.npz"
BOUNDARY_PATH = "data/processed/boundary.json"


def load_split(path=SPLIT_PATH):
    with open(path) as f:
        return json.load(f)


def build_tensors(
    clean_h5_path=OMICS_PATH,
    genes_path=SELECTED_GENES_PATH,
    split_path=SPLIT_PATH,
    scaler_path=SCALER_PATH,
    boundary_path=BOUNDARY_PATH,
):
    tx, mt = read_omics_clean(clean_h5_path)
    genes = pd.read_csv(genes_path)["symbol"].tolist()

    tx = tx[genes]
    assert tx.shape[1] == 5000, f"expected 5000, got {tx.shape[1]}"

    X = pd.concat([tx, mt], axis=1)
    boundary = tx.shape[1]
    assert X.shape == (904, 5225), f"expected (904, 5225), got {X.shape}"

    split = load_split(split_path)

    folds = {}
    for name, ids in split.items():
        folds[name] = X.loc[ids]

    expected = {"train": 723, "val": 90, "test": 91}
    for name, f in folds.items():
        assert (
            len(f) == expected[name]
        ), f"{name}: expected {expected[name]}, got {len(f)}"

    scaler = Standardizer().fit(folds["train"])

    tensors = {}
    for name, f in folds.items():
        transformed = scaler.transform(f)
        tensors[name] = transformed.astype("float64")

    scaler.save(scaler_path)
    with open(boundary_path, "w") as fh:
        json.dump(
            {"boundary": boundary, "tx": boundary, "mt": X.shape[1] - boundary},
            fh,
            indent=2,
        )
    print(f"folds: " + ", ".join(f"{k}={v.shape}" for k, v in tensors.items()))
    print(f"boundary (tx|mt): {boundary} | {X.shape[1] - boundary}")
    print(f"scaler -> {scaler_path}")
    return tensors, boundary


if __name__ == "__main__":
    build_tensors()
