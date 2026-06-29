import torch
import torch.nn.functional as F


def vae_loss(recon_tx, recon_mt, x_tx, x_mt, mu, logvar, beta):
    recon_tx_loss = F.mse_loss(recon_tx, x_tx, reduction="mean")
    recon_mt_loss = F.mse_loss(recon_mt, x_mt, reduction="mean")
    kl_per_dim = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp())
    kl = kl_per_dim.mean()
    total = recon_tx_loss + recon_mt_loss + beta * kl
    return total, recon_tx_loss, recon_mt_loss, kl
