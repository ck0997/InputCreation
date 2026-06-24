#!/usr/bin/env python3
"""Build MacroEnergy CO2 pipeline and injection input CSVs.

This script updates two MacroEnergy asset files:

* co2_pipeline.csv: pipeline investment and transport costs
* co2_injection.csv: injection investment and operational costs

The default paths are repo-relative so the command can be run from any
directory inside this repository.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


HOURS_PER_YEAR = 8760
TONS_PER_MEGATON = 1_000_000

# Pipeline costs are expressed in the units expected by the MacroEnergy asset
# schema. Operational cost is the model variable O&M transport cost.
PIPELINE_ONSHORE_INVESTMENT_COST = (3.7 * 1.14) / (HOURS_PER_YEAR * 500)
PIPELINE_OFFSHORE_INVESTMENT_COST = (6.0 * 1.14) / (HOURS_PER_YEAR * 500)
PIPELINE_OPERATIONAL_COST_FRACTION = 0.03

# Injection cost assumptions from the injection cost workbook/notebook.
INJECTION_COST_ASSUMPTIONS = {
    "Cdr ($/m)": 28275.0,
    "Cfx ($)": 8917500.0,
    "Cfc ($)": 6655500.0,
    "Csd ($)": 26205487.5,
    "Cme ($)": 1663875.0,
    "Cac (%)": 0.05,
}
INJECTION_OPERATIONAL_COST_FRACTION = 0.03

BASIN_INPUTS = [
    {"Basin": "Songliao Basin", "Median Depth (m)": 1500, "Injection Rate (Mt/a)": 0.42, "Injection Rate (Mt/a) Max": 1.64},
    {"Basin": "Turpan-Hami Basin", "Median Depth (m)": 3000, "Injection Rate (Mt/a)": 10.26, "Injection Rate (Mt/a) Max": 28.63},
    {"Basin": "Subei Basin", "Median Depth (m)": 1750, "Injection Rate (Mt/a)": 13.58, "Injection Rate (Mt/a) Max": 34.07},
    {"Basin": "Bohai Bay Basin (onshore)", "Median Depth (m)": 2250, "Injection Rate (Mt/a)": 23.82, "Injection Rate (Mt/a) Max": 122.77},
    {"Basin": "Qaidam Basin", "Median Depth (m)": 3000, "Injection Rate (Mt/a)": 9.43, "Injection Rate (Mt/a) Max": 17.56},
    {"Basin": "Nanxiang Basin", "Median Depth (m)": 2250, "Injection Rate (Mt/a)": 14.86, "Injection Rate (Mt/a) Max": 124.67},
    {"Basin": "Sanjiang Basin", "Median Depth (m)": 2000, "Injection Rate (Mt/a)": 50.05, "Injection Rate (Mt/a) Max": 94.65},
    {"Basin": "Hailar Basin", "Median Depth (m)": 1750, "Injection Rate (Mt/a)": 0.02, "Injection Rate (Mt/a) Max": 0.06},
    {"Basin": "Jianghan Basin", "Median Depth (m)": 2000, "Injection Rate (Mt/a)": 0.08, "Injection Rate (Mt/a) Max": 0.31},
    {"Basin": "Tarim Basin", "Median Depth (m)": 2000, "Injection Rate (Mt/a)": 5.78, "Injection Rate (Mt/a) Max": 32.5},
    {"Basin": "Ordos Basin", "Median Depth (m)": 2250, "Injection Rate (Mt/a)": 0.1, "Injection Rate (Mt/a) Max": 0.79},
    {"Basin": "Ejinjina Basin", "Median Depth (m)": 1500, "Injection Rate (Mt/a)": 0.05, "Injection Rate (Mt/a) Max": 0.12},
    {"Basin": "Hehuai Basin", "Median Depth (m)": 2500, "Injection Rate (Mt/a)": 3.58, "Injection Rate (Mt/a) Max": 51.87},
    {"Basin": "Qinshui Basin", "Median Depth (m)": 1100, "Injection Rate (Mt/a)": 0.12, "Injection Rate (Mt/a) Max": 0.17},
    {"Basin": "Erlian Basin", "Median Depth (m)": 900, "Injection Rate (Mt/a)": 4.56, "Injection Rate (Mt/a) Max": 14.67},
    {"Basin": "Junggar Basin", "Median Depth (m)": 2500, "Injection Rate (Mt/a)": 0.8, "Injection Rate (Mt/a) Max": 2.28},
    {"Basin": "Sichuan Basin", "Median Depth (m)": 1900, "Injection Rate (Mt/a)": 0.01, "Injection Rate (Mt/a) Max": 0.02},
    {"Basin": "Bohai Bay Basin (offshore)", "Median Depth (m)": 1450, "Injection Rate (Mt/a)": 16.81, "Injection Rate (Mt/a) Max": 34.44},
    {"Basin": "North Yellow Sea Basin", "Median Depth (m)": 1500, "Injection Rate (Mt/a)": 14.77, "Injection Rate (Mt/a) Max": 67.35},
    {"Basin": "South Yellow Sea Basin", "Median Depth (m)": 2500, "Injection Rate (Mt/a)": 0.07, "Injection Rate (Mt/a) Max": 0.61},
    {"Basin": "East China Sea Basin", "Median Depth (m)": 1600, "Injection Rate (Mt/a)": 12.0, "Injection Rate (Mt/a) Max": 61.65},
    {"Basin": "Pearl River Mouth Basin", "Median Depth (m)": 1500, "Injection Rate (Mt/a)": 9.3, "Injection Rate (Mt/a) Max": 104.24},
    {"Basin": "Beibu Gulf Basin", "Median Depth (m)": 1500, "Injection Rate (Mt/a)": 24.92, "Injection Rate (Mt/a) Max": 101.3},
    {"Basin": "Qiongdongnan Basin", "Median Depth (m)": 2250, "Injection Rate (Mt/a)": 44.43, "Injection Rate (Mt/a) Max": 134.4},
]

PIPELINE_INVESTMENT_COL = "edges--transmission_edge--investment_cost"
PIPELINE_VARIABLE_OM_COL = "edges--transmission_edge--variable_om_cost"
PIPELINE_START_VERTEX_COL = "edges--transmission_edge--start_vertex"
PIPELINE_END_VERTEX_COL = "edges--transmission_edge--end_vertex"

INJECTION_STORAGE_VERTEX_COL = "edges--co2_storage_edge--end_vertex"
INJECTION_INVESTMENT_TARGET_COL = "edges--co2_captured_edge--investment_cost"
INJECTION_OPERATIONAL_TARGET_COL = "edges--co2_captured_edge--variable_om_cost"

INJECTION_INVESTMENT_SOURCE_COL = "Unit Cost of Injection ($/(t/hr)) - investment cost"
INJECTION_OPERATIONAL_SOURCE_COL = "Operational cost"

ROUTE_NAME_ALIASES = {
    "Bohai Bay Basin (onshore)": "BohaiOnshore",
    "Bohai Bay Basin (offshore)": "BohaiOffshore",
    "Sichuan Basin": "SichuanBasin",
}

BASIN_NAME_ALIASES = {
    **ROUTE_NAME_ALIASES,
    "Turpan-Hami Basin": "TurpanHami",
    "Yingen-Ejina Basin": "YingenEjina",
    "Ejinjina Basin": "YingenEjina",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def clean_node_name(value: object) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", str(value)).lower()


def strip_basin_suffix(name: str) -> str:
    return name.removesuffix(" Basin")


def route_node_key(value: object) -> str:
    name = ROUTE_NAME_ALIASES.get(str(value), str(value))
    return clean_node_name(strip_basin_suffix(name))


def model_node_key(value: object) -> str:
    name = re.sub(r"^Region\d+", "", str(value))
    return clean_node_name(name)


def pipeline_start_key(vertex: object) -> str:
    name = str(vertex)
    for prefix in ("co2_captured_", "co2_storage_"):
        if name.startswith(prefix):
            name = name.removeprefix(prefix)
            break
    return model_node_key(name)


def pipeline_end_key(vertex: object) -> str:
    return model_node_key(str(vertex).split("_to_")[-1])


def basin_key(value: object) -> str:
    name = BASIN_NAME_ALIASES.get(str(value), str(value))
    return clean_node_name(strip_basin_suffix(name))


def storage_vertex_key(value: object) -> str:
    return clean_node_name(str(value).removeprefix("co2_storage_"))


def require_columns(df: pd.DataFrame, required_columns: set[str], table_name: str) -> None:
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"{table_name} is missing columns: {sorted(missing_columns)}")


def calculate_pipeline_route_costs(routes: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        routes,
        {"start", "end", "onshore_km", "offshore_km", "mean_surface_cost"},
        "routes",
    )
    route_costs = routes.copy()
    route_costs["investment_cost"] = (
        PIPELINE_ONSHORE_INVESTMENT_COST
        * route_costs["onshore_km"]
        * route_costs["mean_surface_cost"]
        + PIPELINE_OFFSHORE_INVESTMENT_COST * route_costs["offshore_km"]
    )
    route_costs["operational_cost"] = (
        PIPELINE_OPERATIONAL_COST_FRACTION
        * PIPELINE_ONSHORE_INVESTMENT_COST
        * route_costs["onshore_km"]
        + PIPELINE_OPERATIONAL_COST_FRACTION
        * PIPELINE_OFFSHORE_INVESTMENT_COST
        * route_costs["offshore_km"]
    )
    return route_costs


def build_route_cost_lookup(routes: pd.DataFrame) -> pd.DataFrame:
    route_costs = calculate_pipeline_route_costs(routes).assign(
        _start_key=lambda df: df["start"].map(route_node_key),
        _end_key=lambda df: df["end"].map(route_node_key),
    )[["_start_key", "_end_key", "investment_cost", "operational_cost"]]

    duplicated = route_costs.duplicated(["_start_key", "_end_key"], keep=False)
    if duplicated.any():
        raise ValueError(
            "Duplicate route keys found:\n"
            + route_costs.loc[duplicated, ["_start_key", "_end_key"]].to_string(index=False)
        )
    return route_costs


def update_pipeline_csv(template_path: Path, routes_path: Path, output_path: Path) -> int:
    pipeline = pd.read_csv(template_path, dtype=str)
    routes = pd.read_csv(routes_path)
    route_costs = build_route_cost_lookup(routes)

    require_columns(
        pipeline,
        {
            "id",
            PIPELINE_START_VERTEX_COL,
            PIPELINE_END_VERTEX_COL,
            PIPELINE_INVESTMENT_COL,
            PIPELINE_VARIABLE_OM_COL,
        },
        str(template_path),
    )

    matched = pipeline.assign(
        _start_key=pipeline[PIPELINE_START_VERTEX_COL].map(pipeline_start_key),
        _end_key=pipeline[PIPELINE_END_VERTEX_COL].map(pipeline_end_key),
    ).merge(
        route_costs,
        on=["_start_key", "_end_key"],
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    unmatched = matched[matched["_merge"] != "both"]
    if not unmatched.empty:
        raise ValueError(
            "Some CO2 pipeline rows could not be matched to routes:\n"
            + unmatched[["id", PIPELINE_START_VERTEX_COL, PIPELINE_END_VERTEX_COL]].to_string(index=False)
        )

    matched[PIPELINE_INVESTMENT_COL] = matched["investment_cost"]
    matched[PIPELINE_VARIABLE_OM_COL] = matched["operational_cost"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matched[pipeline.columns].to_csv(output_path, index=False)
    return len(matched)


def calculate_injection_costs() -> pd.DataFrame:
    costs = pd.DataFrame(BASIN_INPUTS)
    costs["Injection Rate (t/hr) Mean"] = (
        costs["Injection Rate (Mt/a)"] * TONS_PER_MEGATON / HOURS_PER_YEAR
    )
    costs["Injection Rate (t/hr) Max"] = (
        costs["Injection Rate (Mt/a) Max"] * TONS_PER_MEGATON / HOURS_PER_YEAR
    )

    for column, value in INJECTION_COST_ASSUMPTIONS.items():
        costs[column] = value

    costs["Costj(WellFixed) ($)"] = (
        costs["Cdr ($/m)"] * costs["Median Depth (m)"]
        + costs["Cfx ($)"]
        + costs["Cfc ($)"]
    ) * (1 + costs["Cac (%)"])
    costs["Costj(ResFixed) ($)"] = (costs["Csd ($)"] + costs["Cme ($)"]) * (
        1 + costs["Cac (%)"]
    )
    costs["Cj(WF) + Cj(RF) ($)"] = (
        costs["Costj(WellFixed) ($)"] + costs["Costj(ResFixed) ($)"]
    )
    costs[INJECTION_INVESTMENT_SOURCE_COL] = (
        costs["Cj(WF) + Cj(RF) ($)"] / costs["Injection Rate (t/hr) Mean"]
    )
    costs["Unit Cost of Injection ($/(Mt/year)) Mean"] = (
        costs["Cj(WF) + Cj(RF) ($)"] / costs["Injection Rate (Mt/a)"]
    )
    costs["Unit Cost of Injection ($/(Mt/year)) Max"] = (
        costs["Cj(WF) + Cj(RF) ($)"] / costs["Injection Rate (Mt/a) Max"]
    )
    costs["Mean to Max Unit Cost Ratio"] = (
        costs["Unit Cost of Injection ($/(Mt/year)) Mean"]
        / costs["Unit Cost of Injection ($/(Mt/year)) Max"]
    )
    costs[INJECTION_OPERATIONAL_SOURCE_COL] = (
        costs[INJECTION_INVESTMENT_SOURCE_COL] * INJECTION_OPERATIONAL_COST_FRACTION
    )
    return costs


def build_injection_cost_lookup(injection_costs: pd.DataFrame) -> pd.DataFrame:
    lookup = injection_costs.assign(
        _basin_key=injection_costs["Basin"].map(basin_key),
    )[["_basin_key", "Basin", INJECTION_INVESTMENT_SOURCE_COL, INJECTION_OPERATIONAL_SOURCE_COL]]

    duplicated = lookup.duplicated("_basin_key", keep=False)
    if duplicated.any():
        raise ValueError(
            "Duplicate basin keys found:\n"
            + lookup.loc[duplicated, ["Basin", "_basin_key"]].to_string(index=False)
        )
    return lookup


def update_injection_csv(
    template_path: Path,
    output_path: Path,
    injection_costs_path: Path | None = None,
) -> int:
    injection = pd.read_csv(template_path, dtype=str)
    injection_costs = calculate_injection_costs()
    lookup = build_injection_cost_lookup(injection_costs)

    require_columns(
        injection,
        {
            "id",
            INJECTION_STORAGE_VERTEX_COL,
            INJECTION_INVESTMENT_TARGET_COL,
            INJECTION_OPERATIONAL_TARGET_COL,
        },
        str(template_path),
    )

    matched = injection.assign(
        _basin_key=injection[INJECTION_STORAGE_VERTEX_COL].map(storage_vertex_key),
    ).merge(
        lookup,
        on="_basin_key",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    unmatched = matched[matched["_merge"] != "both"]
    if not unmatched.empty:
        raise ValueError(
            "Some CO2 injection rows could not be matched to basin costs:\n"
            + unmatched[["id", INJECTION_STORAGE_VERTEX_COL]].to_string(index=False)
        )

    matched[INJECTION_INVESTMENT_TARGET_COL] = matched[INJECTION_INVESTMENT_SOURCE_COL]
    matched[INJECTION_OPERATIONAL_TARGET_COL] = matched[INJECTION_OPERATIONAL_SOURCE_COL]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matched[injection.columns].to_csv(output_path, index=False)

    if injection_costs_path is not None:
        injection_costs_path.parent.mkdir(parents=True, exist_ok=True)
        injection_costs.to_csv(injection_costs_path, index=False)

    return len(matched)


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(
        description="Build CO2 pipeline and injection cost input CSVs for MacroEnergy."
    )
    parser.add_argument(
        "--pipeline-template",
        type=Path,
        default=root / "data" / "processed" / "co2" / "co2_pipeline.csv",
        help="Input co2_pipeline.csv schema/template to update.",
    )
    parser.add_argument(
        "--injection-template",
        type=Path,
        default=root / "data" / "processed" / "co2" / "co2_injection.csv",
        help="Input co2_injection.csv schema/template to update.",
    )
    parser.add_argument(
        "--routes",
        type=Path,
        default=root / "data" / "raw" / "co2" / "routes_export.csv",
        help="Route table with start/end, onshore/offshore km, and mean surface cost.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "data" / "processed" / "co2",
        help="Directory for generated MacroEnergy asset CSVs.",
    )
    parser.add_argument(
        "--injection-costs-output",
        type=Path,
        default=root / "data" / "processed" / "co2" / "injection_basin_costs.csv",
        help="Optional supporting table with basin-level injection calculations.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline_rows = update_pipeline_csv(
        args.pipeline_template,
        args.routes,
        args.output_dir / "co2_pipeline.csv",
    )
    injection_rows = update_injection_csv(
        args.injection_template,
        args.output_dir / "co2_injection.csv",
        args.injection_costs_output,
    )
    print(f"Wrote {pipeline_rows} pipeline rows to {args.output_dir / 'co2_pipeline.csv'}")
    print(f"Wrote {injection_rows} injection rows to {args.output_dir / 'co2_injection.csv'}")
    print(f"Wrote basin injection costs to {args.injection_costs_output}")


if __name__ == "__main__":
    main()
