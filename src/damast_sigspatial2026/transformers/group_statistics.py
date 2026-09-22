"""
damast plugin transformer: derive per-vessel and fleet-wide AIS reporting-gap statistics.

This file is not part of the damast package - it is picked up as a local plugin via the
DAMAST_PLUGIN_PATH mechanism (see damast.core.transformations.PluginManager), which makes
'ExtractGroupStatistics' resolvable by module_name='group_statistics' both when building
the pipeline and when it is later replayed with `damast process`.
"""
import polars as pl

import damast
from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import PipelineElement


class ExtractGroupStatistics(PipelineElement):
    """
    Compute AIS ping-gap (delta_time) statistics per vessel and for the whole fleet, and
    export them (vessel-stats, fleet-stats, fleet-analysis) into `self.parent_pipeline.base_dir`.
    """

    @damast.core.describe("Extract per-vessel and fleet-wide delta_time statistics")
    @damast.core.input({"group": {"representation_type": int},
                        "delta_time": {"representation_type": float}})
    @damast.core.output({})
    def transform(self, df: AnnotatedDataFrame) -> AnnotatedDataFrame:
        group = self.get_name("group")
        delta_time = self.get_name("delta_time")

        vessel_stats = (
            df.group_by(group)
            .agg([
                pl.len().alias("total_pings"),
                pl.col(delta_time).mean().alias("avg_delta"),
                pl.col(delta_time).median().alias("median_delta"),
                pl.col(delta_time).std().alias("std_delta"),
                pl.col(delta_time).min().alias("min_delta"),
                pl.col(delta_time).max().alias("max_delta"),
                # Share of pings whose predecessor gap exceeds a given threshold
                (pl.col(delta_time) > 60).mean().alias("gap_ratio_1min"),
                (pl.col(delta_time) > 5 * 60).mean().alias("gap_ratio_5min"),
                (pl.col(delta_time) > 15 * 60).mean().alias("gap_ratio_15min"),
                (pl.col(delta_time) > 60 * 60).mean().alias("gap_ratio_1h"),
            ])
        )

        fleet_stats = df.select([
            # Global data volume
            pl.len().alias("total_fleet_pings"),
            pl.col(group).n_unique().alias("unique_vessels"),

            # Global distribution (all pings treated equally)
            pl.col(delta_time).mean().alias("fleet_avg_delta"),
            pl.col(delta_time).median().alias("fleet_median_delta"),
            pl.col(delta_time).max().alias("absolute_max_gap"),

            # Percentiles, useful for data-quality/SLA style reporting
            pl.col(delta_time).quantile(0.90).alias("p90_delta"),
            pl.col(delta_time).quantile(0.95).alias("p95_delta"),
        ])

        fleet_analysis = (
            df.group_by(group)
            .agg([
                pl.col(delta_time).median().alias("vessel_median"),
                pl.col(delta_time).max().alias("vessel_max_gap"),
            ])
            .select([
                # Typical reporting interval across the fleet
                pl.col("vessel_median").mean().alias("avg_vessel_reporting_interval"),
                # Worst-case gap for a typical vessel
                pl.col("vessel_max_gap").median().alias("median_vessel_max_gap"),
                pl.col("vessel_max_gap").max().alias("worst_vessel_max_gap"),
            ])
        )

        output_dir = self.parent_pipeline.base_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, dataframe in {
            "vessel-stats": vessel_stats,
            "fleet-stats": fleet_stats,
            "fleet-analysis": fleet_analysis,
        }.items():
            metadata = AnnotatedDataFrame.infer_annotation(dataframe)
            AnnotatedDataFrame(dataframe, metadata).export(
                output_dir / f"ais-{name}.parquet"
            )

        return df
