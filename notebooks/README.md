# Notebooks

These notebooks are kept for provenance and review. The repeatable workflow for
creating the final CSVs is `scripts/build_co2_cost_inputs.py`.

## Files

- `methodology_anna2.ipynb` - exploratory least-cost path and candidate CO2 pipeline route development. The reusable route output used by the script is `data/raw/co2/routes_export.csv`.
- `co2_injection_costs.ipynb` - exploratory injection-cost calculation. The reusable assumptions and formulas are now consolidated in `scripts/build_co2_cost_inputs.py`.

## When To Use These

Use the notebooks when you want to inspect or revise the research methodology.
Use the Python script when you want to regenerate the final MacroEnergy-ready
CSV files.
