import torch
import torch.nn as nn


class Encoder(nn.Module):
    def __init__(self, tx_dim=5000, mt_dim=225, latent_dim=128):
        super().__init__()
        self.tx_trunk = nn.Sequential(
            nn.Linear(tx_dim, 1024),
            nn.LayerNorm(1024),
            nn.GELU(),
            nn.Linear(1024, 256),
            nn.LayerNorm(256),
            nn.GELU(),
        )

        self.mt_trunk = nn.Sequential(
            nn.Linear(mt_dim, 128), nn.LayerNorm(128), nn.GELU()
        )

        self.shared_head = nn.Sequential(
            nn.Linear(256 + 128, 256), nn.LayerNorm(256), nn.GELU()
        )

        self.mu = nn.Linear(256, latent_dim)
        self.logvar = nn.Linear(256, latent_dim)

    def forward(self, x_tx, x_mt):
        h_t = self.tx_trunk(x_tx)
        h_m = self.mt_trunk(x_mt)
        h = torch.concat([h_t, h_m], dim=1)
        s = self.shared_head(h)
        return self.mu(s), self.logvar(s)


class ShallowEncoder(nn.Module):
    def __init__(self, tx_dim, mt_dim, latent_dim, tx_hidden, mt_hidden):
        super().__init__()
        self.tx_trunk = nn.Sequential(
            nn.Linear(tx_dim, tx_hidden), nn.LayerNorm(tx_hidden), nn.GELU()
        )
        self.mt_trunk = nn.Sequential(
            nn.Linear(mt_dim, mt_hidden), nn.LayerNorm(mt_hidden), nn.GELU()
        )
        concat = tx_hidden + mt_hidden
        self.mu = nn.Linear(concat, latent_dim)
        self.logvar = nn.Linear(concat, latent_dim)

    def forward(self, x_tx, x_mt):
        h_t = self.tx_trunk(x_tx)
        h_m = self.mt_trunk(x_mt)
        h = torch.concat([h_t, h_m], dim=1)
        return self.mu(h), self.logvar(h)
