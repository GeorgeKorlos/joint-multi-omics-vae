import yaml
import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader

from src.data.pipeline import build_tensors
from src.model.vae import VAE
from src.model.losses import vae_loss

CONFIG_TRAINING_PATH = "config/training.yaml"


def load_config(path=CONFIG_TRAINING_PATH):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["training"]


def make_loader(arr, batch_size, shuffle, device):
    arr = arr.values  # DataFrame -> numpy (N, 5225), float64
    t = torch.tensor(arr, dtype=torch.float32, device=device)
    ds = TensorDataset(t)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)


def run_epoch(model, loader, tx_dim, beta, optimizer=None):
    train = optimizer is not None
    model.train() if train else model.eval()

    total_sum = 0.0
    tx_sum = 0.0
    mt_sum = 0.0
    kl_sum = 0.0

    n_samples = len(loader.dataset)

    for (x,) in loader:
        x_tx = x[:, :tx_dim]
        x_mt = x[:, tx_dim:]

        with torch.set_grad_enabled(train):
            recon_tx, recon_mt, mu, logvar = model(x)

            total, rtx, rmt, kl = vae_loss(
                recon_tx, recon_mt, x_tx, x_mt, mu, logvar, beta
            )

        if train:
            optimizer.zero_grad()
            total.backward()
            optimizer.step()

        batch_size = x.size(0)

        total_sum += total.item() * batch_size
        tx_sum += rtx.item() * batch_size
        mt_sum += rmt.item() * batch_size
        kl_sum += kl.item() * batch_size

    total_avg = total_sum / n_samples
    tx_avg = tx_sum / n_samples
    mt_avg = mt_sum / n_samples
    kl_avg = kl_sum / n_samples

    return total_avg, tx_avg, mt_avg, kl_avg


def main():
    cfg = load_config()
    torch.manual_seed(cfg["seed"])
    np.random.seed(cfg["seed"])
    device = cfg["device"]
    tensors, boundary = build_tensors()
    train_loader = make_loader(tensors["train"], cfg["batch_size"], True, device)
    val_loader = make_loader(tensors["val"], cfg["batch_size"], False, device)
    model = VAE(tx_dim=boundary, mt_dim=5225 - boundary, latent_dim=128).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    for epoch in range(cfg["epochs"]):
        tr = run_epoch(model, train_loader, boundary, cfg["beta"], optimizer)
        va = run_epoch(model, val_loader, boundary, cfg["beta"], optimizer=None)
        print(
            f"epoch {epoch:3d} | "
            f"train total {tr[0]:.4f} tx {tr[1]:.4f} mt {tr[2]:.4f} kl {tr[3]:.4f} | "
            f"val total {va[0]:.4f} tx {va[1]:.4f} mt {va[2]:.4f} kl {va[3]:.4f}"
        )
    return model


if __name__ == "__main__":
    main()
