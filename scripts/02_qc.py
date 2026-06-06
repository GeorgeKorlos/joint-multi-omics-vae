import yaml
import h5py
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent

cfg = yaml.safe_load((REPO_ROOT / "config" / "base.yaml").open())

tx_path = REPO_ROOT / cfg["paths"]["raw_transcriptomics"]
mt_path = REPO_ROOT / cfg["paths"]["raw_metabolomics"]
processed_dir = REPO_ROOT / cfg["paths"]["data_processed"]
logs_dir = REPO_ROOT / cfg["paths"]["logs"]

processed_dir.mkdir(parents=True, exist_ok=True)
logs_dir.mkdir(parents=True, exist_ok=True)

outlier_sd = cfg["qc"]["outlier_sd"]
min_paired = cfg["qc"]["min_paired"]

transcriptomics = pd.read_csv(tx_path, index_col=0)
transcriptomics.index.name = "DepMap_ID"
transcriptomics.columns = transcriptomics.columns.str.replace(
    r"\s*\(\d+\)\s*$", "", regex=True
)


metabolomics = pd.read_csv(mt_path)
metabolomics = metabolomics.drop(columns=["CCLE_ID"])
metabolomics = metabolomics.set_index("DepMap_ID")
metabolomics = metabolomics.apply(pd.to_numeric, errors="coerce")


assert transcriptomics.shape == (1684, 19205)
assert metabolomics.shape == (928, 225)


common = transcriptomics.index.intersection(metabolomics.index)
tx = transcriptomics.loc[common]
mt = metabolomics.loc[common]

assert len(common) == 912

# Per-sample total on the joined transcriptomics only
tx_total = tx.sum(axis=1)

# z-score
tx_z = (tx_total - tx_total.mean()) / tx_total.std(ddof=0)

outlier_mask = tx_z < -outlier_sd
removed_ids = tx_total.index[outlier_mask].tolist()

expected_outliers = {
    "ACH-000544",
    "ACH-000732",
    "ACH-000002",
    "ACH-000979",
    "ACH-000646",
    "ACH-000415",
    "ACH-000771",
    "ACH-000794",
}

assert (
    set(removed_ids) == expected_outliers
), f"Contract broken: got {sorted(removed_ids)}"


# Drop from both
tx_clean = tx.loc[~outlier_mask]
mt_clean = mt.loc[~outlier_mask]

assert len(tx_clean) >= min_paired, f"Below floor: {len(tx_clean)} < {min_paired}"
assert len(tx_clean) == 904

# Index allignment check
assert tx_clean.index.equals(mt_clean.index)

# save to h5py


def write_df_h5(group, df):
    group.create_dataset(
        "data", data=df.to_numpy(dtype=np.float64), dtype=np.float64, compression="gzip"
    )
    str_dt = h5py.string_dtype(encoding="utf-8")
    group.create_dataset("index", data=df.index.astype(str).to_numpy(), dtype=str_dt)

    group.create_dataset(
        "columns", data=df.columns.astype(str).to_numpy(), dtype=str_dt
    )


path = processed_dir / "omics_clean.h5"


with h5py.File(path, "w") as f:
    write_df_h5(f.create_group("tx_clean"), tx_clean)
    write_df_h5(f.create_group("mt_clean"), mt_clean)

print("QC complete")
print(f"  Paired N:        {len(common)} -> {len(tx_clean)}")
print(f"  Removed:         {len(removed_ids)} samples")
print(f"  Removed IDs:     {sorted(removed_ids)}")
print(f"  Genes retained:  {tx_clean.shape[1]}")
print(f"  Metabolites:     {mt_clean.shape[1]}")
print(f"  Output:          {path}")

log_line = (
    f"{datetime.now().isoformat(timespec='seconds')} "
    f"N {len(common)}->{len(tx_clean)} removed={len(removed_ids)} "
    f"genes={tx_clean.shape[1]} metabolites={mt_clean.shape[1]}\n"
)
with (logs_dir / "qc.log").open("a") as f:
    f.write(log_line)
