# CO2 Pipeline and Injection Cost Methodology

This note documents the reusable CSV generation workflow in
`scripts/build_co2_cost_inputs.py`.

## Pipeline Costs

The route input is `data/raw/co2/routes_export.csv`. Each row contains a
least-cost path segment between a province or storage basin pair, including:

- `onshore_km`
- `offshore_km`
- `mean_surface_cost`

The script calculates:

- investment cost = onshore unit cost * onshore km * mean surface cost + offshore unit cost * offshore km
- operational cost = 3 percent of the unit investment cost multiplied by route length

These values are written into:

- `edges--transmission_edge--investment_cost`
- `edges--transmission_edge--fixed_om_cost`

## Injection Costs

The basin-level assumptions are stored as constants in
`scripts/build_co2_cost_inputs.py` so they can be reviewed in one place.

For each basin, the script calculates:

- mean injection rate in t/hr from Mt/year
- well fixed cost
- reservoir fixed cost
- unit injection investment cost in dollars per t/hr
- operational cost as 3 percent of the investment cost

These values are written into:

- `edges--co2_captured_edge--investment_cost`
- `edges--co2_captured_edge--fixed_om_cost`

The detailed basin-level calculation is also exported to
`data/processed/co2/injection_basin_costs.csv`.
