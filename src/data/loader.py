import torch
from torch.utils.data import TensorDataset, DataLoader


def make_loader(arr, batch_size, shuffle, device):
    arr = arr.values  # DataFrame -> numpy (N, 5225), float64

    t = torch.tensor(arr, dtype=torch.float32, device=device)

    ds = TensorDataset(t)

    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)
