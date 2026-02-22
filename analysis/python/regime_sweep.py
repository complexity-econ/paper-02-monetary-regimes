"""
Paper-02: Bifurcation diagram comparison — PLN vs EUR.
Overlays both regimes on same axes to show how critical point shifts.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9, 'legend.fontsize': 9,
    'figure.dpi': 200, 'savefig.dpi': 200, 'savefig.bbox': 'tight',
})

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "figures"
OUT_DIR.mkdir(exist_ok=True)

BDP_LEVELS = list(range(0, 5001, 250))

PLN_COLOR = '#2196F3'
EUR_COLOR = '#E91E63'

def load_sweep(regime):
    """Load all sweep terminal CSVs for a given regime."""
    d = ROOT / "simulations" / "results" / regime
    rows = []
    for bdp in BDP_LEVELS:
        fpath = d / f"sweep_{regime}_{bdp}_terminal.csv"
        if not fpath.exists():
            print(f"  MISSING: {fpath.name}")
            continue
        df = pd.read_csv(fpath, sep=";", decimal=",")
        for _, row in df.iterrows():
            eff_bdp = row.get('EffectiveBDP', bdp)
            if pd.isna(eff_bdp):
                eff_bdp = bdp
            rows.append({
                'BDP': bdp,
                'Adoption': row['TotalAdoption'] * 100,
                'Inflation': row['Inflation'] * 100,
                'Unemployment': row['Unemployment'] * 100,
                'ExRate': row['ExRate'],
                'RefRate': row['RefRate'] * 100,
                'NPL': row['NPL'] * 100,
                'EffectiveBDP': eff_bdp,
            })
    return pd.DataFrame(rows)

print("Loading PLN sweep...")
data_pln = load_sweep("pln")
print(f"  {len(data_pln)} datapoints")

print("Loading EUR sweep...")
data_eur = load_sweep("eur")
print(f"  {len(data_eur)} datapoints")


# ═══════════════════════════════════════════════════════════════
# FIGURE 1: 2×2 bifurcation comparison
# ═══════════════════════════════════════════════════════════════

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

def plot_bifurcation(ax, col, ylabel, title):
    for data, color, label in [(data_pln, PLN_COLOR, 'PLN (NBP)'),
                                (data_eur, EUR_COLOR, 'EUR (ECB)')]:
        if data.empty:
            continue
        ax.scatter(data['BDP'], data[col], c=color, alpha=0.15, s=10, edgecolor='none')
        means = data.groupby('BDP')[col].agg(['mean', 'std'])
        ax.plot(means.index, means['mean'], color=color, linewidth=2.5,
                label=label, zorder=5)
        ax.fill_between(means.index, means['mean'] - means['std'],
                         means['mean'] + means['std'],
                         color=color, alpha=0.1)
    ax.set_xlabel("UBI (PLN/month)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight='bold')
    ax.set_xlim(-100, 5100)
    ax.legend(loc='best')

plot_bifurcation(axes[0, 0], 'Adoption',
                 "Technology adoption M120 (%)", "A. Adoption bifurcation")
plot_bifurcation(axes[0, 1], 'Inflation',
                 "Inflation M120 (%)", "B. Inflation bifurcation")
axes[0, 1].axhline(y=0, color='gray', linewidth=0.5, linestyle=':')

plot_bifurcation(axes[1, 1], 'Unemployment',
                 "Unemployment M120 (%)", "D. Unemployment bifurcation")

# Panel C: Variance comparison — critical point signature
ax = axes[1, 0]
for data, color, label in [(data_pln, PLN_COLOR, 'PLN'),
                            (data_eur, EUR_COLOR, 'EUR')]:
    if data.empty:
        continue
    stds = data.groupby('BDP')['Adoption'].std()
    ax.plot(stds.index, stds.values, color=color, linewidth=2.5,
            marker='o', markersize=4, label=label)
    # Mark critical point
    if not stds.empty:
        cp = stds.idxmax()
        ax.axvline(x=cp, color=color, linestyle='--', alpha=0.4, linewidth=1)
        ax.annotate(f'{cp}', (cp, stds[cp]), textcoords="offset points",
                    xytext=(8, 5), fontsize=8, color=color, fontweight='bold')

ax.set_xlabel("UBI (PLN/month)")
ax.set_ylabel("σ of adoption (%)")
ax.set_title("C. Critical point signature (max variance)", fontweight='bold')
ax.legend()

fig.suptitle("Bifurcation: PLN vs EUR — sweep 0–5,000 PLN (30 seeds × 21 points)",
             fontsize=13, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig(OUT_DIR / "p02_bifurcation_comparison.png")
print("\nSaved: p02_bifurcation_comparison.png")
plt.close()


# ═══════════════════════════════════════════════════════════════
# FIGURE 2: Regime difference (EUR - PLN) across BDP sweep
# ═══════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

for idx, (col, ylabel, title) in enumerate([
    ('Adoption', 'Δ Adoption (pp)', 'A. Adoption difference'),
    ('Inflation', 'Δ Inflation (pp)', 'B. Inflation difference'),
    ('Unemployment', 'Δ Unemployment (pp)', 'C. Unemployment difference'),
]):
    ax = axes[idx]
    if not data_pln.empty and not data_eur.empty:
        m_pln = data_pln.groupby('BDP')[col].mean()
        m_eur = data_eur.groupby('BDP')[col].mean()
        common = m_pln.index.intersection(m_eur.index)
        diff = m_eur.loc[common] - m_pln.loc[common]
        ax.bar(common, diff, width=200, color=['#4CAF50' if d > 0 else '#F44336' for d in diff],
               alpha=0.7, edgecolor='white')
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.set_xlabel("UBI (PLN/month)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontweight='bold')

fig.suptitle("EUR − PLN difference across UBI sweep",
             fontsize=12, fontweight='bold', y=1.02)
fig.tight_layout()
fig.savefig(OUT_DIR / "p02_regime_difference.png")
print("Saved: p02_regime_difference.png")
plt.close()


# ═══════════════════════════════════════════════════════════════
# Summary table
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 100)
print("SWEEP COMPARISON SUMMARY")
print("=" * 100)
print(f"{'BDP':>6s} | {'PLN Adopt':>9s} {'±σ':>5s} {'EUR Adopt':>9s} {'±σ':>5s} | "
      f"{'PLN Infl':>9s} {'EUR Infl':>9s} | "
      f"{'PLN Unemp':>9s} {'EUR Unemp':>9s} | "
      f"{'EUR EffBDP':>10s}")
print("-" * 115)

for bdp in BDP_LEVELS:
    pln_sub = data_pln[data_pln['BDP'] == bdp]
    eur_sub = data_eur[data_eur['BDP'] == bdp]
    if pln_sub.empty or eur_sub.empty:
        continue
    eur_eff = eur_sub['EffectiveBDP'].mean() if 'EffectiveBDP' in eur_sub.columns else bdp
    print(f"{bdp:6d} | "
          f"{pln_sub.Adoption.mean():9.1f} {pln_sub.Adoption.std():5.1f} "
          f"{eur_sub.Adoption.mean():9.1f} {eur_sub.Adoption.std():5.1f} | "
          f"{pln_sub.Inflation.mean():9.1f} {eur_sub.Inflation.mean():9.1f} | "
          f"{pln_sub.Unemployment.mean():9.1f} {eur_sub.Unemployment.mean():9.1f} | "
          f"{eur_eff:10.0f}")

# Critical points
for data, label in [(data_pln, 'PLN'), (data_eur, 'EUR')]:
    if data.empty:
        continue
    stds = data.groupby('BDP')['Adoption'].std()
    cp = stds.idxmax()
    print(f"\nCritical point ({label}): BDP = {cp} PLN  (σ_adopt = {stds[cp]:.1f}%)")

print("\nDone!")
