#!/usr/bin/env python
"""
Build, run and save the 'ais_prepare' damast pipeline.

This is the plugin-based conversion of ais-analysis/ais-prepare.py: it derives per-ping
kinematic features (delta_time/delta_distance/speed/heading/angular_velocity), cyclic time/
lat/lon encodings, and a HEALPix bin id, from raw AIS pings.

The only custom transformer needed here (Healpix) is not part of the damast package - it is
loaded as a local plugin via the DAMAST_PLUGIN_PATH mechanism (damast.core.transformations.
PluginManager) from the 'transformers/' folder next to this script, same as build_pipeline.py.
ParseTimestamp is reused from that same folder. Building the pipeline this way keeps the saved
*.damast.ppl file replayable via the generic `damast process` CLI on any machine, as long as
DAMAST_PLUGIN_PATH points at that same 'transformers/' folder - see README.md for the exact
commands.
"""
import logging
import os
from argparse import ArgumentParser
from pathlib import Path

try:
    # The package has to be installed, otherwise these need to be available as local plugin
    from damast.plugins import Healpix, ParseTimestamp
    breakpoint()
except ImportError:
    breakpoint()
    # The package has not been installed, so enabling as local plugin
    PLUGIN_DIR = Path(__file__).parent / "transformers"
    os.environ.setdefault("DAMAST_PLUGIN_PATH", str(PLUGIN_DIR))

from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import DataProcessingPipeline
from damast.core.metadata import ValidationMode
from damast.data_handling.transformers import AddDeltaTime
from damast.data_handling.transformers.cycle_transformer import (
    CycleTransformer,
    TimestampCycleTransformer,
)
from damast.data_handling.transformers.filters import FilterWithin
from damast.domains.maritime.transformers import (
    AngularVelocity,
    DeltaDistance,
    Heading,
    Speed,
)
from damast.utils.io import Archive

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=str, required=True,
                        help="Directory for the saved pipeline (*.damast.ppl) and its results")
    parser.add_argument("--pipeline-name", type=str, default="ais_prepare")
    parser.add_argument("--ship-types", nargs="+", type=int, default=[30, 60, 70, 80],
                        help="AIS ship-type codes to keep (default: cargo/tanker/passenger types)")
    parser.add_argument("--healpix-nside", type=int, default=128)

    subparsers = parser.add_subparsers(help="sub-command help", dest='command')
    parser_run = subparsers.add_parser('run', help="Run the pipeline")
    parser_run.add_argument("--ais-data", nargs="+", type=str, required=True,
                        help="AIS input file(s), e.g. a .parquet file")

    parser_run = subparsers.add_parser('export', help="Export the pipeline")
    args = parser.parse_args()

    base_dir = Path(args.output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    pipeline = (
        DataProcessingPipeline(name=args.pipeline_name, base_dir=base_dir)
        .add("parse_timestamp", ParseTimestamp(),
             name_mappings={"from": "msgtime", "to": "timestamp"})
        .add("filter_ship_types", FilterWithin(within_values=args.ship_types),
             name_mappings={"x": "shipType"})
        .add("delta_time", AddDeltaTime(),
             name_mappings={"group": "mmsi", "time_column": "timestamp"})
        .add("delta_distance", DeltaDistance(x_shift=True, y_shift=True),
             name_mappings={
                 "group": "mmsi", "sort": "timestamp",
                 "x": "latitude", "y": "longitude", "out": "delta_distance",
             })
        .add("speed", Speed(),
             name_mappings={"delta_distance": "delta_distance", "delta_time": "delta_time"})
        .add("heading", Heading(),
             name_mappings={
                 "group": "mmsi", "sort": "timestamp",
                 "lat": "latitude", "lon": "longitude", "heading": "heading",
             })
        .add("angular_velocity", AngularVelocity(),
             name_mappings={"group": "mmsi", "time": "timestamp", "heading": "heading"})
        .add("cycle_timestamp", TimestampCycleTransformer(), name_mappings={"x": "timestamp"})
        .add("lat_cycle_transform", CycleTransformer(n=180), name_mappings={"x": "latitude"})
        .add("lon_cycle_transform", CycleTransformer(n=360), name_mappings={"x": "longitude"})
        .add("healpix", Healpix(nside=args.healpix_nside))
    )

    if args.command == 'export':
        pipeline_file = pipeline.save(dir=base_dir)
        print(f"Saved pipeline: {pipeline_file}")
    elif args.command == 'run':
        with Archive(filenames=args.ais_data) as input_files:
            ais_files = [x for x in input_files if AnnotatedDataFrame.get_supported_format(Path(x).suffix)]

        # UPDATE_METADATA: input may already carry stats/bounds for a column this pipeline
        # recomputes (e.g. when chained after another ais-analyse script) - refresh them to match
        # the freshly computed values instead of erroring out (READONLY) or dropping rows (UPDATE_DATA)
        ais_adf = AnnotatedDataFrame.from_files(
            ais_files, metadata_required=False, validation_mode=ValidationMode.UPDATE_METADATA
        )

        new_adf = pipeline.transform(df=ais_adf)

        output_file = base_dir / f"{args.pipeline_name}.parquet"
        new_adf.export(output_file)
        logger.info(f"Created: {output_file}")

        print(pipeline.to_str(indent_level=2))
        print(new_adf.head(10).collect())
    else:
        print(f"Unknown subcommand {args.command}")
