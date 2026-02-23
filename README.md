# Monetary Regime and the Acceleration Paradox

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18740933.svg)](https://doi.org/10.5281/zenodo.18740933)

**PLN vs EUR counterfactual**: Does the acceleration paradox require monetary sovereignty?

## Summary

Paper-01 showed a phase transition at UBI = 2,000 PLN driven by NBP's endogenous Taylor rule and floating exchange rate. This paper tests whether the mechanism survives under Eurozone membership, where the ECB sets rates exogenously and the exchange rate is fixed.

**Key question**: Is monetary sovereignty a prerequisite for the acceleration paradox?

## Method

Same SFC-ABM as Paper-01 (10,000 firms × 6 sectors × Watts-Strogatz network × 120 months), with two monetary regimes:

| | PLN (NBP) | EUR (ECB) |
|---|---|---|
| Interest rate | Endogenous Taylor rule | Exogenous ECB Taylor rule (reacts to Eurozone inflation, not Polish) |
| Exchange rate | Floating, BoP-driven | Fixed at 4.33 PLN/EUR |
| Import prices | ER pass-through | No ER pass-through |
| Capital account | IRP arbitrage | Single monetary zone |

Full parameter sweep: 21 UBI levels (0–5,000 PLN) × 2 regimes × 30 seeds = **1,260 simulations**.

## Reproduce

Requires [complexity-econ/core](https://github.com/complexity-econ/core) (Scala 3 + sbt).

```bash
# Quick test (3 seeds)
cd ../core && sbt "run 2000 3 test_pln pln" && sbt "run 2000 3 test_eur eur"

# Full sweep
make simulate   # ~30 min

# Generate figures
make figures
```

## Structure

```
analysis/python/        Analysis & plotting scripts
figures/                Generated figures (PNG, 200 DPI)
latex/                  Paper (XeLaTeX)
simulations/results/    CSV output (pln/, eur/)
simulations/scripts/    Sweep runner
```

## Dependencies

- **Simulation**: [complexity-econ/core](https://github.com/complexity-econ/core) (Scala 3.5.2, sbt 1.10.6)
- **Analysis**: Python 3 (matplotlib, seaborn, scipy, numpy, pandas)
- **Paper**: XeLaTeX + biblatex

## License

MIT

## Related

- [Paper-01: The Acceleration Paradox](https://github.com/complexity-econ/paper-01-acceleration-paradox) — foundation model
- [Core engine](https://github.com/complexity-econ/core) — reusable SFC-ABM
