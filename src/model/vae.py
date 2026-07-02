import torch
import torch.nn as nn
from src.model.encoder import Encoder, ShallowEncoder
from src.model.decoder import LinearDecoder


class VAE(nn.Module):
    def __init__(self, tx_dim, mt_dim, latent_dim, arch, tx_hidden, mt_hidden):
        super().__init__()
        self.tx_dim = tx_dim
        if arch == "asymmetric":
            self.encoder = Encoder(tx_dim, mt_dim, latent_dim)
        elif arch == "shallow":
            self.encoder = ShallowEncoder(
                tx_dim, mt_dim, latent_dim, tx_hidden, mt_hidden
            )
        else:
            raise ValueError(f"unknown arch: {arch}")
        self.decoder = LinearDecoder(tx_dim, mt_dim, latent_dim)

    def reparameterize(self, mu, logvar):
        if not self.training:
            return mu
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        x_tx = x[:, : self.tx_dim]
        x_mt = x[:, self.tx_dim :]
        mu, logvar = self.encoder(x_tx, x_mt)
        z = self.reparameterize(mu, logvar)
        recon_tx, recon_mt = self.decoder(z)
        return recon_tx, recon_mt, mu, logvar
