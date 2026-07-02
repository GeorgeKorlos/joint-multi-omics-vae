import torch
import numpy as np


def collect_latents(model, test_arr, tx_dim, device):
    x = torch.tensor(test_arr.values, dtype=torch.float32, device=device)
    model.eval()
    with torch.no_grad():
        x_tx = x[:, :tx_dim]
        x_mt = x[:, tx_dim:]
        mu, logvar = model.encoder(x_tx, x_mt)
        recon_tx, recon_mt, _, _ = model(x)

    return mu, logvar, x_tx, x_mt, recon_tx, recon_mt


def posterior_collapse(mu, logvar, threshold=0.01):
    kl_per_dim = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp())
    kl_per_dim = kl_per_dim.mean(dim=0)
    n_active = (kl_per_dim > threshold).sum().item()
    return n_active, kl_per_dim


def r2_per_modality(x_tx, x_mt, recon_tx, recon_mt):
    res_tx = ((x_tx - recon_tx) ** 2).sum()
    tot_tx = ((x_tx - x_tx.mean(dim=0)) ** 2).sum()
    r2_tx = (1 - res_tx / tot_tx).item()

    res_mt = ((x_mt - recon_mt) ** 2).sum()
    tot_mt = ((x_mt - x_mt.mean(dim=0)) ** 2).sum()
    r2_mt = (1 - res_mt / tot_mt).item()

    return r2_tx, r2_mt


def main():
    from src.training.trainer import train as train_main, load_config
    from src.data.pipeline import build_tensors

    cfg = load_config()
    device = cfg["device"]

    model, _ = train_main(beta=1)
    tensors, boundary = build_tensors()

    mu, logvar, x_tx, x_mt, rtx, rmt = collect_latents(
        model, tensors["test"], boundary, device
    )

    n_active, kl_vec = posterior_collapse(mu, logvar)
    r2_tx, r2_mt = r2_per_modality(x_tx, x_mt, rtx, rmt)

    print(f"active latent dims: {n_active} / 128")
    print(f"R2 tx: {r2_tx:.4f}  |  R2 mt: {r2_mt:.4f}")
    print(
        f"KL per dim — min {kl_vec.min():.4f} max {kl_vec.max():.4f} median {kl_vec.median():.4f}"
    )


if __name__ == "__main__":
    main()
