import h5py
import pandas as pd

EXPECTED_SHAPES = {"tx_clean": (904, 19205), "mt_clean": (904, 225)}
OMICS_PATH = "data/processed/omics_clean.h5"


def _read_group(f, name):
    g = f[name]
    data = g["data"][:]
    cols = g["columns"][:].astype(str)
    idx = g["index"][:].astype(str)

    df = pd.DataFrame(data, idx, cols)
    exp = EXPECTED_SHAPES[name]
    assert (
        df.shape == exp
    ), f"{name}: expected {exp}, got {df.shape} (stale/re-synced source?)"
    return df


def read_omics_clean(path=OMICS_PATH):
    with h5py.File(path, "r") as f:
        tx = _read_group(f, "tx_clean")
        mt = _read_group(f, "mt_clean")
        assert list(tx.index) == list(mt.index), "tx/mt sample order mismatch"
    return tx, mt
