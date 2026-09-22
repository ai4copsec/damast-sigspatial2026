#!/usr/bin/env python
"""
Build, run and save the 'ais_join_sources' damast pipeline.

Combines AIS data from different sources, e.g., marine-cadastre and barentswatch, into one
dataframe with a common schema. Every data source gets its own branch, which aligns its columns to
the canonical AIS schema (AlignAISSchema, configured per source in ais-sources.yaml), and the
branches are then stacked row-wise (ConcatDataFrames) via pipeline joins.

Example:
    python 0-join-sources.py --output-dir results/joined run \\
        --input aisdk:data/aisdk-2026-06-01.parquet \\
        --input marine-cadastre:data/ais-2026-01-01.parquet \\
        --input barentswatch:data/AIS_2026_06_01.parquet

    # only save the pipeline, e.g. for a replay via 'damast process'
    python 0-join-sources.py --output-dir results/joined export --sources aisdk marine-cadastre barentswatch
"""
import logging
from argparse import ArgumentParser
from pathlib import Path

import yaml
from damast.core.transformations import plugin_manager

# see 0-prepare.py: register the local 'transformers/' folder if this package is not installed
PLUGIN_PACKAGE = "damast_sigspatial2026"
if PLUGIN_PACKAGE not in plugin_manager.plugin_packages():
    plugin_manager.register_plugin_package(PLUGIN_PACKAGE, Path(__file__).parent / "transformers")

from damast.core.constants import DAMAST_DEFAULT_DATASOURCE
from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import DataProcessingPipeline
from damast.core.metadata import ValidationMode
from damast.plugins.damast_sigspatial2026 import AlignAISSchema, ConcatDataFrames

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def parse_inputs(inputs: list[str]) -> dict[str, list[str]]:
    """Group '<datasource>:<file>' arguments by datasource, keeping the order of first appearance."""
    files: dict[str, list[str]] = {}
    for arg in inputs:
        source, sep, filename = arg.partition(":")
        if not sep or not filename:
            raise ValueError(f"--input expects '<datasource>:<file>', got '{arg}'")
        files.setdefault(source, []).append(filename)
    return files


def source_pipeline(source: str, config: dict, base_dir: Path) -> DataProcessingPipeline:
    """Single-step pipeline aligning one source to the canonical AIS schema."""
    # damast only validates name_mappings against real data (in transform), so an 'export' would
    # otherwise save a pipeline whose mapping gaps/typos only surface on replay
    problems = []
    if missing := set(AlignAISSchema.SCHEMA) - set(config["columns"]):
        problems.append(f"no column mapping for {sorted(missing)}")
    if unknown := set(config["columns"]) - set(AlignAISSchema.SCHEMA):
        problems.append(f"mapping for unknown column(s) {sorted(unknown)}")
    if problems:
        raise ValueError(f"Source '{source}': {' and '.join(problems)}")

    return DataProcessingPipeline(name=source, base_dir=base_dir).add(
        f"align_{source}",
        AlignAISSchema(source=source,
                       timestamp_format=config["timestamp_format"],
                       scale=config.get("scale")),
        name_mappings={f"{AlignAISSchema.SOURCE_PREFIX}{name}": column for name, column in config["columns"].items()},
    )


def build_pipeline(name: str, sources: list[str], config: dict, base_dir: Path) -> DataProcessingPipeline:
    """The first source is the pipeline's default datasource, every further one is joined in."""
    pipeline = source_pipeline(sources[0], config[sources[0]], base_dir)
    pipeline.name = name
    for source in sources[1:]:
        pipeline.join(source, ConcatDataFrames(),
                      data_source=source_pipeline(source, config[source], base_dir),
                      name_mappings={"df": {}, "other": {}})
    return pipeline


def load_source(files: list[str]) -> AnnotatedDataFrame:
    return AnnotatedDataFrame.from_files(files, metadata_required=False,
                                         validation_mode=ValidationMode.UPDATE_METADATA)


def check_sources(parser: ArgumentParser, sources: list[str], config: dict, config_file: str):
    unknown = set(sources) - set(config)
    if unknown:
        parser.error(f"unknown source(s) {sorted(unknown)} - known: {sorted(config)} (see {config_file})")
    if len(set(sources)) < 2:
        parser.error("at least two different sources are required")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=str, required=True,
                        help="Directory for the saved pipeline (*.damast.ppl) and its result")
    parser.add_argument("--pipeline-name", type=str, default="ais_join_sources")
    parser.add_argument("--sources-config", type=str, default=Path(__file__).parent / "ais-sources.yaml",
                        help="YAML file with the column mapping per source (default: ais-sources.yaml)")

    subparsers = parser.add_subparsers(help="sub-command help", dest="command", required=True)
    parser_run = subparsers.add_parser("run", help="Run (and save) the pipeline")
    parser_run.add_argument("--input", action="append", required=True, metavar="SOURCE:FILE",
                            help="Input file of a known source, e.g. 'barentswatch:data/AIS_2026_08_01.parquet'."
                                 " Repeat for more files/sources - at least two sources are required")
    parser_export = subparsers.add_parser("export", help="Save the pipeline only")
    parser_export.add_argument("--sources", nargs="+", metavar="SOURCE",
                               help="Sources to join, the first one being the default datasource"
                                    " (default: all sources in --sources-config)")
    args = parser.parse_args()

    with open(args.sources_config) as f:
        config = yaml.safe_load(f)

    if args.command == "run":
        files = parse_inputs(args.input)
        sources = list(files)
    else:
        sources = args.sources or list(config)
    check_sources(parser, sources, config, args.sources_config)

    base_dir = Path(args.output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    pipeline = build_pipeline(args.pipeline_name, sources, config, base_dir)
    pipeline_file = pipeline.save(dir=base_dir)

    if args.command == "export":
        print(f"Saved pipeline: {pipeline_file}")
        # the first source is the pipeline's default datasource, named 'df'
        input_data = " ".join([f"--input-data {DAMAST_DEFAULT_DATASOURCE}=<{sources[0]}-files>",
                               *[f"--input-data {source}=<{source}-files>" for source in sources[1:]]])
        print(f"Replay with: damast process --pipeline {pipeline_file} {input_data}")
    else:
        logger.info(f"Saved pipeline: {pipeline_file}")
        adf = pipeline.transform(df=load_source(files[sources[0]]),
                                 **{source: load_source(files[source]) for source in sources[1:]})

        output_file = base_dir / f"{args.pipeline_name}.parquet"
        adf.export(output_file)
        logger.info(f"Created: {output_file}")

        print(pipeline.to_str(indent_level=2))
        print(adf.head(10).collect())
