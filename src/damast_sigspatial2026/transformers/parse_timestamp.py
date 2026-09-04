"""
damast plugin transformer: parse an AIS string timestamp (with UTC offset, e.g. 'msgtime')
into a proper polars Datetime column.

This file is not part of the damast package - it is picked up as a local plugin via the
DAMAST_PLUGIN_PATH mechanism (see damast.core.transformations.PluginManager), which makes
'ParseTimestamp' resolvable by module_name='parse_timestamp' both when building the pipeline
and when it is later replayed with `damast process`.
"""
import damast
import polars as pl
from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import PipelineElement


class ParseTimestamp(PipelineElement):
    """
    Parse a string timestamp column into a timezone-aware polars Datetime column.
    """

    timeformat: str

    def __init__(self, *, timeformat: str = "%Y-%m-%dT%H:%M:%S%:z"):
        self.timeformat = timeformat

    @damast.core.describe("Parse a string timestamp into a polars Datetime column")
    @damast.core.input({"from": {"representation_type": str}})
    @damast.core.output({"to": {"representation_type": pl.Datetime}})
    def transform(self, df: AnnotatedDataFrame) -> AnnotatedDataFrame:
        from_name = self.get_name("from")
        to_name = self.get_name("to")

        df.lazyframe = df.lazyframe.filter(
            pl.col(from_name).is_not_null()
        ).with_columns(
            # AIS feeds report a variable (and sometimes overlong) number of fractional-second
            # digits, e.g. '...57.6118424+00:00' - drop them since timeformat has no '%f'
            pl.col(from_name).str.replace(r"\.\d+", "").alias(from_name)
        ).with_columns(
            pl.col(from_name).str.to_datetime(self.timeformat).alias(to_name)
        )
        return df
