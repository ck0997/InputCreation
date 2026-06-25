# InputCreation

Reusable input-building, notebook, and plotting files for MacroEnergy CO2
pipeline transport and injection workflows.

## Quick Links

Final MacroEnergy-ready input CSVs:

- [`data/processed/co2/co2_pipeline.csv`](data/processed/co2/co2_pipeline.csv) - CO2 pipeline investment costs and transport variable O&M costs.
- [`data/processed/co2/co2_injection.csv`](data/processed/co2/co2_injection.csv) - CO2 injection investment costs and operational costs.
- [`data/processed/co2/injection_basin_costs.csv`](data/processed/co2/injection_basin_costs.csv) - basin-level injection cost calculations used to update `co2_injection.csv`.

Main reusable script:

- [`scripts/build_co2_cost_inputs.py`](scripts/build_co2_cost_inputs.py)

Methodology notebooks:

- [`notebooks/co2_pipeline_costs/co2/co2_pipelines_cost.ipynb`](notebooks/co2_pipeline_costs/co2/co2_pipelines_cost.ipynb)
- [`notebooks/co2_injection_costs.ipynb`](notebooks/co2_injection_costs.ipynb)

Plotting workflow:

- [`plots/plot_co2_capture_transport_storage.py`](plots/plot_co2_capture_transport_storage.py)
- [`plots/plot_results.ipynb`](plots/plot_results.ipynb)
- [`plots/plot_injection_rate_impact.ipynb`](plots/plot_injection_rate_impact.ipynb)

## What This Repo Is For

This repo keeps the CO2 input-creation workflow easy to inspect and reuse.
The final CSVs in `data/processed/co2/` can be copied directly into a
MacroEnergy `assets/assets_1/` folder for the China CO2 transport and storage
case.

The notebooks document the research process and route-development methodology.
The Python script is the repeatable path for regenerating the final CSVs.

## Repository Map

- `data/processed/co2/` - final generated MacroEnergy-ready input CSVs.
- `scripts/` - reusable command-line generation scripts.
- `docs/` - concise methodology notes and column mappings.
- `notebooks/` - exploratory and provenance notebooks.
- `notebooks/co2_pipeline_costs/co2/` - CO2 pipeline route-development notebook and supporting route input files.
- `plots/` - plotting notebooks, plotting helper script, and example result files.

## Regenerate CO2 Cost CSVs

You only need to run the builder when route inputs, cost assumptions, or asset
templates change. If you just need the current inputs, use the CSVs already in
`data/processed/co2/`.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the builder from the repo root:

```bash
python scripts/build_co2_cost_inputs.py
```

By default, the script reads route information from:

```text
notebooks/co2_pipeline_costs/co2/routes_export.csv
```

and writes regenerated files to:

```text
data/processed/co2/
```

To update a separate MacroEnergy asset folder directly:

```bash
python scripts/build_co2_cost_inputs.py \
  --pipeline-template /path/to/assets/assets_1/co2_pipeline.csv \
  --injection-template /path/to/assets/assets_1/co2_injection.csv \
  --routes notebooks/co2_pipeline_costs/co2/routes_export.csv \
  --output-dir /path/to/assets/assets_1
```

## Cost Columns Updated

The builder updates these MacroEnergy columns:

- pipeline investment cost: `edges--transmission_edge--investment_cost`
- pipeline transport cost: `edges--transmission_edge--variable_om_cost`
- injection investment cost: `edges--co2_captured_edge--investment_cost`
- injection operational cost: `edges--co2_captured_edge--variable_om_cost`

## Plotting

The `plots/` folder contains notebooks and helper code for reviewing CO2
capture, transport, storage, and injection-rate impacts. The included
`plots/results_016/` folder is an example MacroEnergy results directory used by
the plotting notebooks.
