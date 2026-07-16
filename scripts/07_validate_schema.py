import h5py
import numpy as np

OUT_PATH = "data/embeddings/omics_embeddings.h5"


with h5py.File(OUT_PATH, "r") as f:
    protein_emb = f["protein_embeddings"][()]  # type: ignore[index]
    metabolite_emb = f["metabolite_embeddings"][()]  # type: ignore[index]
    protein_ids = f["protein_ids"].asstr()[()]  # type: ignore[attr-defined]
    metabolite_ids = f["metabolite_ids"].asstr()[()]  # type: ignore[attr-defined]
    p_meta = dict(f["protein_metadata"].attrs)
    m_meta = dict(f["metabolite_metadata"].attrs)
    g_meta = dict(f["global_metadata"].attrs)

    assert protein_emb.dtype == np.float32  # type: ignore
    assert protein_emb.shape == (4958, 128)  # type: ignore
    assert np.allclose(np.linalg.norm(protein_emb, axis=1), 1.0, atol=1e-5)  # type: ignore
    assert len(protein_ids) == protein_emb.shape[0]  # type: ignore
    assert not any("-" in a for a in protein_ids)
    assert len(set(protein_ids)) == len(protein_ids)
    print("schema validation passed")
