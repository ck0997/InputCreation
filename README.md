# InputCreation

Reusable input-building tools for MacroEnergy lab workflows.

## New CO2 Cost Inputs

The ready-to-use CSVs are here:

- [`data/processed/co2/co2_pipeline.csv`](data/processed/co2/co2_pipeline.csv) - CO2 pipeline investment costs and transport variable O&M costs.
- [`data/processed/co2/co2_injection.csv`](data/processed/co2/co2_injection.csv) - CO2 injection investment costs and operational costs.
- [`data/processed/co2/injection_basin_costs.csv`](data/processed/co2/injection_basin_costs.csv) - supporting basin-level injection cost calculations.

Copy `co2_pipeline.csv` and `co2_injection.csv` into a MacroEnergy
`assets/assets_1/` directory when running the China CO2 transport and storage
case.

## Repository Map

- `scripts/build_co2_cost_inputs.py` - reusable command-line builder for the new CSVs.
- `data/raw/co2/routes_export.csv` - least-cost pipeline route table used to calculate pipeline costs.
- `data/raw/co2/province_capitals.csv` - province centroid inputs used in route development.
- `data/raw/co2/basin_centroids.csv` - storage basin centroid inputs used in route development.
- `data/processed/co2/` - final generated MacroEnergy-ready input CSVs.
- `docs/co2_cost_methodology.md` - concise formulas and column mapping.
- `chinny_co2_pipeline_distance/` - exploratory notebook-era route development files kept for traceability.

## Regenerate the CSVs

Install the one Python dependency:

```bash
python -m pip install -r requirements.txt
```

Then run:

```bash
python scripts/build_co2_cost_inputs.py
```

By default, the script reads `data/raw/co2/routes_export.csv`, updates the
template files in `data/processed/co2/`, and writes regenerated files back into
`data/processed/co2/`.

To update a separate MacroEnergy asset folder directly:

```bash
python scripts/build_co2_cost_inputs.py \
  --pipeline-template /path/to/assets/assets_1/co2_pipeline.csv \
  --injection-template /path/to/assets/assets_1/co2_injection.csv \
  --output-dir /path/to/assets/assets_1
```

## Outputs

The builder updates these MacroEnergy columns:

- pipeline investment cost: `edges--transmission_edge--investment_cost`
- pipeline transport cost: `edges--transmission_edge--variable_om_cost`
- injection investment cost: `edges--co2_captured_edge--investment_cost`
- injection operational cost: `edges--co2_captured_edge--variable_om_cost`
