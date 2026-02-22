"""
Paper-02: Regime comparison charts — PLN (NBP) vs EUR (ECB).
Main 6-panel time series for 3 BDP levels, each comparing both regimes.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9, 'legend.fontsize': 8,
    'figure.dpi': 200, 'savefig.dpi': 200, 'savefig.bbox': 'tight',
})

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "figures"
OUT_DIR.mkdir(exist_ok=True)

def load_ts(regime, bdp):
    """Load timeseries CSV for given regime and BDP level."""
    d = ROOT / "simulations" / "results" / regime
    prefix = f"sweep_{regime}_{bdp}"
    return pd.read_csv(d / f"{prefix}_timeseries.csv", sep=";", decimal=",")

def load_term(regime, bdp):
    """Load terminal CSV for given regime and BDP level."""
    d = ROOT / "simulations" / "results" / regime
    prefix = f"sweep_{regime}_{bdp}"
    return pd.read_csv(d / f"{prefix}_terminal.csv", sep=";", decimal=",")

BDP_SHOW = [0, 2000, 3000]
BDP_LABELS = ['UBI = 0', 'UBI = 2,000', 'UBI = 3,000']

# ═══════════════════════════════════════════════════════════════
# FIGURE 1: 6-panel comparison (3 cols = BDP levels, 2 rows = metrics)
#           Each panel: PLN line vs EUR line with CI bands
# ═══════════════════════════════════════════════════════════════

METRICS = [
    ("Inflation",     "Inflation (annual %)",       100),
    ("Unemployment",  "Unemployment (%)",            100),
    ("TotalAdoption", "Technology adoption (%)",     100),
    ("ExRate",        "Exchange rate (PLN/EUR)",      1),
    ("MarketWage",    "Market wage (PLN)",            1),
    ("RefRate",       "Central bank rate (%)",       100),
]

PLN_COLOR = '#2196F3'
EUR_COLOR = '#E91E63'

fig, axes = plt.subplots(3, 3, figsize=(15, 12))

for col_idx, (bdp, bdp_label) in enumerate(zip(BDP_SHOW, BDP_LABELS)):
    try:
        ts_pln = load_ts("pln", bdp)
        ts_eur = load_ts("eur", bdp)
    except FileNotFoundError as e:
        print(f"Missing data for BDP={bdp}: {e}")
        continue

    months = ts_pln["Month"].values

    panel_metrics = [
        ("Inflation",     "Inflation (%)",           100, 0),
        ("TotalAdoption", "Adoption (%)",            100, 0),
        ("Unemployment",  "Unemployment (%)",        100, 0),
    ]

    for row_idx, (col_base, ylabel, mult, hline) in enumerate(panel_metrics):
        ax = axes[row_idx, col_idx]

        for ts, color, label in [(ts_pln, PLN_COLOR, 'PLN (NBP)'),
                                  (ts_eur, EUR_COLOR, 'EUR (ECB)')]:
            mean = ts[f"{col_base}_mean"].values * mult
            p05 = ts[f"{col_base}_p05"].values * mult
            p95 = ts[f"{col_base}_p95"].values * mult
            ax.plot(months, mean, color=color, linewidth=1.5, label=label)
            ax.fill_between(months, p05, p95, color=color, alpha=0.12)

        ax.axvline(x=30, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        if hline is not None:
            ax.axhline(y=hline, color='gray', linestyle=':', linewidth=0.5)
        ax.set_xlim(1, 120)

        if row_idx == 0:
            ax.set_title(bdp_label, fontweight='bold', fontsize=12)
        if col_idx == 0:
            ax.set_ylabel(ylabel)
        if row_idx == 2:
            ax.set_xlabel("Month")
        if row_idx == 0 and col_idx == 2:
            ax.legend(loc='upper right', framealpha=0.9)

fig.suptitle("Monetary Regime Comparison: PLN vs EUR (bands = 90% CI)",
             fontsize=14, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig(OUT_DIR / "p02_regime_timeseries.png")
print("Saved: p02_regime_timeseries.png")
plt.close()


# ═══════════════════════════════════════════════════════════════
# FIGURE 2: 2×3 detail panels — ExRate, RefRate, NPL, Wage, Debt, PriceLevel
# ═══════════════════════════════════════════════════════════════

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

detail_metrics = [
    ("ExRate",     "Exchange rate (PLN/EUR)",  1),
    ("RefRate",    "Central bank rate (%)",   100),
    ("NPL",        "NPL ratio (%)",          100),
    ("MarketWage", "Market wage (PLN)",        1),
    ("GovDebt",    "Public debt (bn PLN)",   1e-9),
    ("PriceLevel", "Price level",              1),
]

# Use BDP=2000 as the main comparison
bdp = 2000
try:
    ts_pln = load_ts("pln", bdp)
    ts_eur = load_ts("eur", bdp)
    months = ts_pln["Month"].values

    for idx, (col_base, ylabel, mult) in enumerate(detail_metrics):
        ax = axes[idx // 3, idx % 3]
        for ts, color, label in [(ts_pln, PLN_COLOR, 'PLN'),
                                  (ts_eur, EUR_COLOR, 'EUR')]:
            mean = ts[f"{col_base}_mean"].values * mult
            p05 = ts[f"{col_base}_p05"].values * mult
            p95 = ts[f"{col_base}_p95"].values * mult
            ax.plot(months, mean, color=color, linewidth=1.5, label=label)
            ax.fill_between(months, p05, p95, color=color, alpha=0.12)

        ax.axvline(x=30, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.set_ylabel(ylabel)
        ax.set_xlim(1, 120)
        if idx >= 3:
            ax.set_xlabel("Month")
        if idx == 0:
            ax.legend(framealpha=0.9)

    fig.suptitle("Regime Detail: UBI = 2,000 PLN — PLN vs EUR (90% CI)",
                 fontsize=13, fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "p02_regime_detail.png")
    print("Saved: p02_regime_detail.png")
except FileNotFoundError as e:
    print(f"Skipping detail panel: {e}")
plt.close()


# ═══════════════════════════════════════════════════════════════
# FIGURE 3: Terminal scatter — adoption vs inflation phase space
# ═══════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

for idx, (bdp, label) in enumerate(zip(BDP_SHOW, BDP_LABELS)):
    ax = axes[idx]
    try:
        t_pln = load_term("pln", bdp)
        t_eur = load_term("eur", bdp)

        ax.scatter(t_pln['TotalAdoption']*100, t_pln['Inflation']*100,
                   c=PLN_COLOR, marker='o', alpha=0.4, s=25, label='PLN')
        ax.scatter(t_eur['TotalAdoption']*100, t_eur['Inflation']*100,
                   c=EUR_COLOR, marker='s', alpha=0.4, s=25, label='EUR')
    except FileNotFoundError:
        pass

    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle=':')
    ax.set_xlabel("Technology adoption (%)")
    if idx == 0:
        ax.set_ylabel("Inflation (%)")
    ax.set_title(label, fontweight='bold')
    if idx == 0:
        ax.legend()

fig.suptitle("Phase space: PLN vs EUR — adoption × inflation",
             fontsize=12, fontweight='bold', y=1.02)
fig.tight_layout()
fig.savefig(OUT_DIR / "p02_regime_phasespace.png")
print("Saved: p02_regime_phasespace.png")
plt.close()


# ═══════════════════════════════════════════════════════════════
# Summary table
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 90)
print("REGIME COMPARISON SUMMARY")
print("=" * 90)
print(f"{'BDP':>6s} {'Regime':>6s} | {'Adopt':>7s} {'±σ':>5s} | {'Infl':>7s} {'±σ':>5s} | "
      f"{'Unemp':>7s} {'±σ':>5s} | {'ExRate':>7s} | {'RefRate':>7s}")
print("-" * 90)

for bdp in BDP_SHOW:
    for regime in ['pln', 'eur']:
        try:
            df = load_term(regime, bdp)
            print(f"{bdp:6d} {regime:>6s} | "
                  f"{df.TotalAdoption.mean()*100:7.1f} {df.TotalAdoption.std()*100:5.1f} | "
                  f"{df.Inflation.mean()*100:7.1f} {df.Inflation.std()*100:5.1f} | "
                  f"{df.Unemployment.mean()*100:7.1f} {df.Unemployment.std()*100:5.1f} | "
                  f"{df.ExRate.mean():7.2f} | "
                  f"{df.RefRate.mean()*100:7.2f}%")
        except FileNotFoundError:
            print(f"{bdp:6d} {regime:>6s} | (missing)")

print("\nDone!")
