from src.training.health import collect_latents, posterior_collapse, r2_per_modality
from src.training.trainer import train, load_config
from src.data.pipeline import build_tensors
from pathlib import Path
import json

ANCHOR_TEST = {"n_active": 128, "r2_tx": 0.4350, "r2_mt": 0.5951}


def evaluate(model, split_arr, boundary, device) -> dict:
    mu, logvar, x_tx, x_mt, recon_tx, recon_mt = collect_latents(
        model, split_arr, boundary, device
    )

    n_active, kl_per_dim = posterior_collapse(mu, logvar, threshold=0.01)

    r2_tx, r2_mt = r2_per_modality(x_tx, x_mt, recon_tx, recon_mt)

    return {
        "n_active": n_active,
        "kl_min": float(kl_per_dim.min()),
        "kl_median": float(kl_per_dim.median()),
        "kl_max": float(kl_per_dim.max()),
        "r2_tx": r2_tx,
        "r2_mt": r2_mt,
    }


def run_one(beta, arch, cfg, tensors, boundary, eval_test=False, seed=None) -> dict:
    model, history = train(beta, arch, seed)

    val = evaluate(model, tensors["val"], boundary, cfg["device"])

    test = (
        evaluate(model, tensors["test"], boundary, cfg["device"]) if eval_test else None
    )

    record = {"beta": beta, "arch": arch, "val": val, "test": test, "history": history}

    out_dir = Path("experiments/sweep")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{arch}_beta{beta}_seed{seed}.json"

    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)

    return record


def ablation():
    cfg = load_config()
    tensors, boundary = build_tensors()
    run_one(
        beta=1,
        arch="shallow",
        cfg=cfg,
        tensors=tensors,
        boundary=boundary,
        eval_test=True,
    )


def seed_ablation():
    cfg = load_config()
    tensors, boundary = build_tensors()
    rows = []
    for arch in ["asymmetric", "shallow"]:
        for seed in [42, 43, 44]:
            rec = run_one(
                beta=1,
                arch=arch,
                cfg=cfg,
                tensors=tensors,
                boundary=boundary,
                eval_test=False,
                seed=seed,
            )
            v = rec["val"]
            rows.append((arch, seed, v["n_active"], v["r2_tx"], v["r2_mt"]))
    print(f"{'arch':<12}{'seed':<6}{'active':<8}{'tx':<9}{'mt':<9}")
    for arch, seed, n, tx, mt in rows:
        print(f"{arch:<12}{seed:<6}{n:<8}{tx:<9.4f}{mt:<9.4f}")


def main():
    cfg = load_config()
    tensors, boundary = build_tensors()
    for beta in [1, 2, 4, 8]:
        run_one(
            beta=beta,
            arch="shallow",
            cfg=cfg,
            tensors=tensors,
            boundary=boundary,
            eval_test=False,
        )


if __name__ == "__main__":
    main()
