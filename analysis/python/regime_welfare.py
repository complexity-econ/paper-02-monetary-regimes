"""
Paper-02: Welfare comparison — PLN vs EUR across BDP levels.
Real consumption, Gini coefficient, Pareto frontier.
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

PLN_COLOR = '#2196F3'
EUR_COLOR = '#E91E63'

POPULATION = 100_000
MPC = 0.82

BDP_LEVELS = list(range(0, 5001, 250))

def load_term(regime, bdp):
    d = ROOT / "simulations" / "results" / regime
    return pd.read_csv(d / f"sweep_{regime}_{bdp}_terminal.csv", sep=";", decimal=",")

def compute_welfare(df, bdp_amount):
    """Compute welfare metrics per seed.
    Uses EffectiveBDP from simulation (after SGP fiscal constraint) if available,
    otherwise falls back to legislated bdp_amount.
    """
    rows = []
    for _, r in df.iterrows():
        unemp = r['Unemployment']
        wage = r['MarketWage']
        price = r['PriceLevel']
        n_emp = int((1 - unemp) * POPULATION)
        n_unemp = POPULATION - n_emp

        # Use actual BDP delivered (after SGP constraint) if available
        actual_bdp = r.get('EffectiveBDP', bdp_amount)
        if pd.isna(actual_bdp):
            actual_bdp = bdp_amount

        y_emp = wage + actual_bdp
        y_unemp = actual_bdp

        total_income = n_emp * y_emp + n_unemp * y_unemp
        real_consumption = total_income * MPC / max(0.01, price)
        real_cons_pc = real_consumption / POPULATION

        # Gini (binary income: employed vs unemployed)
        if total_income > 0 and n_emp > 0 and n_unemp > 0:
            gini = (n_emp * n_unemp * abs(y_emp - y_unemp)) / (POPULATION * total_income)
        else:
            gini = 0.0

        rows.append({
            'real_cons_pc': real_cons_pc,
            'gini': gini,
            'adoption': r['TotalAdoption'] * 100,
            'unemployment': unemp * 100,
        })
    return pd.DataFrame(rows)

# ═══════════════════════════════════════════════════════════════
# Compute welfare for all BDP × regime combinations
# ═══════════════════════════════════════════════════════════════

welfare = []
for bdp in BDP_LEVELS:
    for regime, color in [('pln', PLN_COLOR), ('eur', EUR_COLOR)]:
        try:
            df = load_term(regime, bdp)
            w = compute_welfare(df, bdp)
            welfare.append({
                'BDP': bdp,
                'Regime': regime.upper(),
                'RealConsPc_mean': w.real_cons_pc.mean(),
                'RealConsPc_std': w.real_cons_pc.std(),
                'Gini_mean': w.gini.mean(),
                'Gini_std': w.gini.std(),
                'Adoption_mean': w.adoption.mean(),
                'Unemployment_mean': w.unemployment.mean(),
            })
        except FileNotFoundError:
            pass

wdf = pd.DataFrame(welfare)
pln = wdf[wdf['Regime'] == 'PLN']
eur = wdf[wdf['Regime'] == 'EUR']

print(f"Loaded welfare data: {len(pln)} PLN points, {len(eur)} EUR points")


# ═══════════════════════════════════════════════════════════════
# FIGURE 1: 2×2 welfare comparison
# ═══════════════════════════════════════════════════════════════

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# A: Real consumption per capita vs BDP
ax = axes[0, 0]
for df, color, label in [(pln, PLN_COLOR, 'PLN'), (eur, EUR_COLOR, 'EUR')]:
    if df.empty:
        continue
    ax.plot(df['BDP'], df['RealConsPc_mean'], color=color, linewidth=2.5,
            marker='o', markersize=4, label=label)
    ax.fill_between(df['BDP'],
                     df['RealConsPc_mean'] - df['RealConsPc_std'],
                     df['RealConsPc_mean'] + df['RealConsPc_std'],
                     color=color, alpha=0.15)
ax.set_xlabel("UBI (PLN/month)")
ax.set_ylabel("Real consumption per capita (PLN)")
ax.set_title("A. Real consumption", fontweight='bold')
ax.legend()

# B: Gini vs BDP
ax = axes[0, 1]
for df, color, label in [(pln, PLN_COLOR, 'PLN'), (eur, EUR_COLOR, 'EUR')]:
    if df.empty:
        continue
    ax.plot(df['BDP'], df['Gini_mean'], color=color, linewidth=2.5,
            marker='o', markersize=4, label=label)
    ax.fill_between(df['BDP'],
                     df['Gini_mean'] - df['Gini_std'],
                     df['Gini_mean'] + df['Gini_std'],
                     color=color, alpha=0.15)
ax.set_xlabel("UBI (PLN/month)")
ax.set_ylabel("Gini coefficient")
ax.set_title("B. Inequality", fontweight='bold')
ax.legend()

# C: Pareto frontier — Gini vs Real Consumption
ax = axes[1, 0]
for df, color, label, marker in [(pln, PLN_COLOR, 'PLN', 'o'),
                                   (eur, EUR_COLOR, 'EUR', 's')]:
    if df.empty:
        continue
    ax.scatter(df['RealConsPc_mean'], df['Gini_mean'],
               c=df['BDP'], cmap='viridis', marker=marker,
               s=60, alpha=0.8, edgecolor=color, linewidth=1.5,
               label=label)
    # Connect dots in order
    ax.plot(df['RealConsPc_mean'], df['Gini_mean'],
            color=color, linewidth=1, alpha=0.4, linestyle='--')

ax.set_xlabel("Real consumption per capita (PLN)")
ax.set_ylabel("Gini coefficient")
ax.set_title("C. Equity–efficiency tradeoff", fontweight='bold')
ax.legend()
# Arrow indicating "better"
ax.annotate("", xy=(0.85, 0.15), xytext=(0.65, 0.35),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle="->", color='gray', lw=1.5))
ax.text(0.88, 0.12, 'better', transform=ax.transAxes, fontsize=8, color='gray')

# D: Summary bar chart for BDP=2000
ax = axes[1, 1]
bdp2k_pln = pln[pln['BDP'] == 2000]
bdp2k_eur = eur[eur['BDP'] == 2000]

if not bdp2k_pln.empty and not bdp2k_eur.empty:
    metrics = ['Adoption_mean', 'Unemployment_mean']
    labels_m = ['Adoption (%)', 'Unemployment (%)']
    x = np.arange(len(metrics))
    w = 0.35

    pln_vals = [bdp2k_pln.iloc[0][m] for m in metrics]
    eur_vals = [bdp2k_eur.iloc[0][m] for m in metrics]

    ax.bar(x - w/2, pln_vals, w, color=PLN_COLOR, alpha=0.8, label='PLN', edgecolor='white')
    ax.bar(x + w/2, eur_vals, w, color=EUR_COLOR, alpha=0.8, label='EUR', edgecolor='white')
    ax.set_xticks(x)
    ax.set_xticklabels(labels_m)
    ax.set_ylabel("Value (%)")
    ax.set_title("D. Key metrics at UBI = 2,000", fontweight='bold')
    ax.legend()

fig.suptitle("Welfare Analysis: PLN vs EUR",
             fontsize=13, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig(OUT_DIR / "p02_welfare_comparison.png")
print("Saved: p02_welfare_comparison.png")
plt.close()


# ═══════════════════════════════════════════════════════════════
# Summary table
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 90)
print("WELFARE COMPARISON")
print("=" * 90)
print(f"{'BDP':>6s} | {'PLN Cons':>9s} {'Gini':>6s} | {'EUR Cons':>9s} {'Gini':>6s} | "
      f"{'ΔCons':>7s} {'ΔGini':>6s}")
print("-" * 90)

for bdp in BDP_LEVELS:
    p = pln[pln['BDP'] == bdp]
    e = eur[eur['BDP'] == bdp]
    if p.empty or e.empty:
        continue
    dc = e.iloc[0]['RealConsPc_mean'] - p.iloc[0]['RealConsPc_mean']
    dg = e.iloc[0]['Gini_mean'] - p.iloc[0]['Gini_mean']
    print(f"{bdp:6d} | "
          f"{p.iloc[0]['RealConsPc_mean']:9.0f} {p.iloc[0]['Gini_mean']:6.3f} | "
          f"{e.iloc[0]['RealConsPc_mean']:9.0f} {e.iloc[0]['Gini_mean']:6.3f} | "
          f"{dc:+7.0f} {dg:+6.3f}")

# Find optimal BDP for each regime
for df, label in [(pln, 'PLN'), (eur, 'EUR')]:
    if df.empty:
        continue
    best = df.loc[df['RealConsPc_mean'].idxmax()]
    print(f"\nOptimal BDP ({label}): {best['BDP']:.0f} PLN "
          f"(cons={best['RealConsPc_mean']:.0f}, gini={best['Gini_mean']:.3f})")

print("\nDone!")
