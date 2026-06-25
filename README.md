# InputCreation

Includes packages for updating investment and operational costs for CO2 pipelines and injection for updating co2_pipelines.csv and co2_injection.csv. The main outputs are ready-to-use CSVs for a MacroEnergy `assets/assets_1/` folder.

## Main Files

Use these files if you only need the current inputs:

- [`data/processed/co2/co2_pipeline.csv`](data/processed/co2/co2_pipeline.csv)
- [`data/processed/co2/co2_injection.csv`](data/processed/co2/co2_injection.csv)
- [`data/processed/co2/injection_basin_costs.csv`](data/processed/co2/injection_basin_costs.csv)

The first two are MacroEnergy input files. The basin-cost file is a supporting
table showing the injection cost calculation by sedimentary basin.

## Repository Map

- `scripts/build_co2_cost_inputs.py` - reusable command-line builder for the CO2 cost CSVs.
- `data/processed/co2/` - final generated MacroEnergy-ready input CSVs.
- `docs/co2_cost_methodology.md` - cost-method notes and column mappings.
- `notebooks/co2_pipeline_costs/co2/` - CO2 pipeline route workflow notebook and route input files.
- `notebooks/co2_injection_costs.ipynb` - injection cost workflow notebook.
- `plots/` - plotting notebooks, plotting helper script, and example results folder.

## Regenerate the Inputs

Run this only if the route data, cost assumptions, or MacroEnergy template files
change. If you just need the current inputs, use the CSVs already in
`data/processed/co2/`.

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

From this folder, run:

```bash
python scripts/build_co2_cost_inputs.py
```

The script reads the route table from:

```text
notebooks/co2_pipeline_costs/co2/routes_export.csv
```

and writes the updated files to:

```text
data/processed/co2/
```

## Write Directly to a MacroEnergy Asset Folder

To update a separate MacroEnergy asset folder instead of the local processed
folder:

```bash
python scripts/build_co2_cost_inputs.py \
  --pipeline-template /path/to/assets/assets_1/co2_pipeline.csv \
  --injection-template /path/to/assets/assets_1/co2_injection.csv \
  --routes notebooks/co2_pipeline_costs/co2/routes_export.csv \
  --output-dir /path/to/assets/assets_1
```

This overwrites `co2_pipeline.csv` and `co2_injection.csv` in the output folder.

## What the Script Updates

`scripts/build_co2_cost_inputs.py` updates four MacroEnergy columns:

- `edges--transmission_edge--investment_cost`
- `edges--transmission_edge--fixed_om_cost`
- `edges--co2_captured_edge--investment_cost`
- `edges--co2_captured_edge--fixed_om_cost`

Pipeline costs are calculated from onshore distance, offshore distance, and the
mean surface-cost factor for each route. Injection costs are calculated by basin
using reservoir depth and injection-rate assumptions.

## Plotting

The `plots/` folder contains notebooks and helper code for reviewing CO2
capture, transport, storage, and injection-rate impacts. The included
`plots/results_016/` folder is an example MacroEnergy results directory used by
the plotting notebooks.
