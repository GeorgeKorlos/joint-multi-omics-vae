import torch.nn as nn


class LinearDecoder(nn.Module):
    def __init__(self, tx_dim=5000, mt_dim=225, latent_dim=128):
        super().__init__()
        self.tx_out = nn.Linear(latent_dim, tx_dim)
        self.mt_out = nn.Linear(latent_dim, mt_dim)

    def forward(self, z):
        return self.tx_out(z), self.mt_out(z)
