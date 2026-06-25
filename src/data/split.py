import json
import hashlib
import numpy as np


def make_split(
    ids, seed=42, frac=(0.8, 0.1, 0.1), out_path="data/processed/split.json"
):
    assert abs(sum(frac) - 1.0) < 1e-9, "fractions must sum to 1"
    ids = sorted(ids)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(ids))
    n = len(ids)
    n_train = int(frac[0] * n)
    n_val = int(frac[1] * n)
    train_idx = perm[:n_train]
    val_idx = perm[n_train : n_train + n_val]
    test_idx = perm[n_train + n_val :]
    split = {
        "train": [ids[i] for i in train_idx],
        "val": [ids[i] for i in val_idx],
        "test": [ids[i] for i in test_idx],
    }
    all_ids = split["train"] + split["val"] + split["test"]
    assert len(all_ids) == n, "fold sizes don't sum to n"
    assert set(all_ids) == set(ids), "split is not a clean partition of the input ids"
    with open(out_path, "w") as f:
        json.dump(split, f, indent=2)
    with open(out_path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    print(f"split -> {out_path}")
    print(
        f"  train/val/test: {len(split['train'])}/{len(split['val'])}/{len(split['test'])}"
    )
    print(f"  sha256: {h}")
    return split


if __name__ == "__main__":
    from src.data.io import read_omics_clean

    tx, _ = read_omics_clean()
    make_split(tx.index.tolist())
