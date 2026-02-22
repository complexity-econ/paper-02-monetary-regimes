#!/usr/bin/env bash
set -euo pipefail

# Paper-02: Full sweep — 21 BDP levels × 2 regimes × 30 seeds = 1260 simulations
# Requires: complexity-econ/core built with sbt

CORE_DIR="$(cd "$(dirname "$0")/../../../core" && pwd)"
RESULTS_DIR="$(cd "$(dirname "$0")/../results" && pwd)"
SEEDS=30

BDP_LEVELS=(0 250 500 750 1000 1250 1500 1750 2000 2250 2500 2750 3000 3250 3500 3750 4000 4250 4500 4750 5000)

echo "=== Paper-02: Monetary Regime Sweep ==="
echo "Core: ${CORE_DIR}"
echo "Output: ${RESULTS_DIR}"
echo "Seeds: ${SEEDS}, BDP levels: ${#BDP_LEVELS[@]}, Regimes: 2"
echo "Total simulations: $(( ${#BDP_LEVELS[@]} * 2 * SEEDS ))"
echo ""

cd "${CORE_DIR}"

for regime in pln eur; do
    echo "--- Regime: ${regime} ---"
    for bdp in "${BDP_LEVELS[@]}"; do
        prefix="sweep_${regime}_${bdp}"
        echo -n "  BDP=${bdp} ... "
        sbt -batch -error "run ${bdp} ${SEEDS} ${prefix} ${regime}" > /dev/null 2>&1
        # Move output to paper-02 results
        mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/${regime}/"
        mv "mc/${prefix}_timeseries.csv" "${RESULTS_DIR}/${regime}/"
        echo "done"
    done
done

echo ""
echo "=== Sweep complete ==="
echo "PLN results: ${RESULTS_DIR}/pln/ ($(ls ${RESULTS_DIR}/pln/*.csv 2>/dev/null | wc -l) files)"
echo "EUR results: ${RESULTS_DIR}/eur/ ($(ls ${RESULTS_DIR}/eur/*.csv 2>/dev/null | wc -l) files)"
