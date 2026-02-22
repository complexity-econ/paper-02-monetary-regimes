CORE_DIR := ../core
RESULTS  := simulations/results
FIGURES  := figures

.PHONY: all simulate figures clean

all: simulate figures

simulate:
	bash simulations/scripts/run_all.sh

figures:
	python3 analysis/python/regime_charts.py
	python3 analysis/python/regime_sweep.py
	python3 analysis/python/regime_welfare.py

clean:
	rm -f $(RESULTS)/pln/*.csv $(RESULTS)/eur/*.csv $(FIGURES)/*.png
