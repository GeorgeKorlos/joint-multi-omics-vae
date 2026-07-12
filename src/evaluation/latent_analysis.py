import torch
import pandas as pd


def all_latents(model, X_all, boundary, device="cpu"):
    x = torch.tensor(X_all.values, dtype=torch.float32, device=device)

    model.eval()
    with torch.no_grad():
        x_tx = x[:, :boundary]
        x_mt = x[:, boundary:]
        mu, logvar = model.encoder(x_tx, x_mt)
    mu_df = pd.DataFrame(mu.cpu().numpy(), index=X_all.index)
    logvar_df = pd.DataFrame(logvar.cpu().numpy(), index=X_all.index)
    return mu_df, logvar_df


def decoder_weight_matrices(model):
    W_tx = model.decoder.tx_out.weight.detach().cpu().numpy()
    W_mt = model.decoder.mt_out.weight.detach().cpu().numpy()
    return W_tx, W_mt


def load_lineage(model_csv_path, sample_index):
    df = pd.read_csv(model_csv_path, usecols=["ModelID", "OncotreeLineage"])
    lineage = df.set_index("ModelID")["OncotreeLineage"]
    return lineage.reindex(sample_index)


def modality_energy(W_tx, W_mt):
    tx_e = (W_tx**2).mean(axis=0)
    mt_e = (W_mt**2).mean(axis=0)
    return tx_e, mt_e


def per_sample_mse(model, X_all, boundary, device="cpu"):
    x = torch.tensor(X_all.values, dtype=torch.float32, device=device)
    model.eval()
    with torch.no_grad():
        recon_tx, recon_mt, _, _ = model(x)
        x_tx, x_mt = x[:, :boundary], x[:, boundary:]
        mse_tx = ((x_tx - recon_tx) ** 2).mean(dim=1)
        mse_mt = ((x_mt - recon_mt) ** 2).mean(dim=1)
    return mse_tx.cpu().numpy(), mse_mt.cpu().numpy()
