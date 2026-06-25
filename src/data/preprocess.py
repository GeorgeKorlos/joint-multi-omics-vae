import numpy as np
import pandas as pd
from .io import read_omics_clean, OMICS_PATH

RAW_TX_PATH = "data/raw/OmicsExpressionProteinCodingGenesTPMLogp1.csv"
SELECTED_GENES_PATH = "data/processed/selected_genes.csv"
TOP_N = 5000


def _symbol_entrez_from_raw(raw_tx_path):
    cols = pd.read_csv(raw_tx_path, nrows=0).columns.tolist()
    gene_headers = cols[1:]

    symbols = []
    entrez = []

    for c in gene_headers:
        symbol = c.split("(")[0].strip()
        if "(" in c:
            eid = c.split("(")[-1].rstrip(")").strip()
        else:
            eid = ""

        symbols.append(symbol)
        entrez.append(eid)

    return symbols, entrez


def select_top_genes(
    clean_h5_path=OMICS_PATH,
    raw_tx_path=RAW_TX_PATH,
    out_path=SELECTED_GENES_PATH,
    top_n=TOP_N,
):
    tx, _ = read_omics_clean(clean_h5_path)
    symbols, entrez = _symbol_entrez_from_raw(raw_tx_path)
    assert len(symbols) == tx.shape[1]
    assert symbols == list(tx.columns)

    vr = tx.astype("float64").var(axis=0).to_numpy()
    keep = sorted(range(len(vr)), key=lambda i: (-vr[i], i))[:top_n]

    table = pd.DataFrame(
        {
            "rank": range(1, top_n + 1),
            "symbol": [symbols[i] for i in keep],
            "entrez": [entrez[i] for i in keep],
            "variance": [vr[i] for i in keep],
        }
    )
    table.to_csv(out_path, index=False)

    print(f"selected {top_n} / {len(vr)} genes  (dropped {len(vr) - top_n})")
    print(f"variance at the cut (rank {top_n}): {table['variance'].iloc[-1]:.6g}")
    print(f"zero-variance genes excluded: {int((vr == 0).sum())}")
    print(f"gene list -> {out_path}")

    return table["symbol"].tolist()


class Standardizer:
    def __init__(self) -> None:
        self.mean_ = None
        self.std_ = None

    def fit(self, X):
        X = np.asarray(X, dtype="float64")
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)
        self.std_ = np.where(self.std_ == 0, 1, self.std_)
        return self

    def transform(self, X):
        if self.mean_ is None:
            raise RuntimeError("transform before fit")
        return (X - self.mean_) / self.std_

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def save(self, path):
        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("save before fit")
        np.savez(path, mean=self.mean_, std=self.std_)

    @classmethod
    def load(cls, path):
        d = np.load(path)
        s = cls()
        s.mean_ = d["mean"]
        s.std_ = d["std"]
        return s


if __name__ == "__main__":
    select_top_genes()
