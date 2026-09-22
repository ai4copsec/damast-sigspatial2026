"""
damast plugin transformer: align an AIS source (e.g. marine-cadastre, barentswatch) to a common,
source-independent column schema, so that several sources can be stacked into one dataframe.

The source-specific column names are not hard-coded: every canonical column 'x' is read from
the input 'src_x', which the pipeline maps to the actual source column via name_mappings, e.g.
{'src_timestamp': 'base_date_time'}. See ais-sources.yaml for the mappings of known sources.
"""
import damast
import polars as pl
from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import PipelineElement

#: The canonical AIS schema: column name -> output spec; 'representation_type' is the target dtype
CANONICAL_AIS_SCHEMA: dict[str, dict] = {
    "mmsi":         {"representation_type": pl.Int64},
    "timestamp":    {"representation_type": pl.Datetime(time_unit="us", time_zone="UTC")},
    "latitude":     {"representation_type": pl.Float64, "unit": "deg"},
    "longitude":    {"representation_type": pl.Float64, "unit": "deg"},
    "sog":          {"representation_type": pl.Float64, "description": "speed over ground in knots"},
    "cog":          {"representation_type": pl.Float64, "unit": "deg",
                     "description": "course over ground (360 = not available)"},
    "heading":      {"representation_type": pl.Int64, "unit": "deg",
                     "description": "true heading (511 = not available)"},
    "nav_status":   {"representation_type": pl.Int64, "description": "AIS navigational status code"},
    "ship_type":    {"representation_type": pl.Int64, "description": "AIS ship type code"},
    "imo":          {"representation_type": pl.Int64},
    "call_sign":    {"representation_type": pl.String},
    "name":         {"representation_type": pl.String},
    "length":       {"representation_type": pl.Int64, "unit": "m"},
    "width":        {"representation_type": pl.Int64, "unit": "m"},
    "draught":      {"representation_type": pl.Float64, "unit": "m"},
    "report_class": {"representation_type": pl.String, "description": "AIS transponder class (A/B)"},
}

#: Prefix of the input names, which are mapped to the source column names
SOURCE_PREFIX = "src_"


class AlignAISSchema(PipelineElement):
    """
    Map a source onto the canonical AIS columns (see CANONICAL_AIS_SCHEMA), cast from the
    mapped source columns, plus a 'source' column identifying the origin of each row. The
    output is exclusive, i.e. the source-specific columns are dropped.

    Casting rules: string timestamps are parsed with 'timestamp_format' and normalised to UTC;
    strings cast to integers keep only their digits (e.g. marine-cadastre imo 'IMO9212424');
    numeric columns listed in 'scale' are multiplied after the cast (e.g. barentswatch
    draught is given in 1/10 m).
    """

    #: Exposed on the class, since the plugin namespace only exports the transformer classes
    SCHEMA = CANONICAL_AIS_SCHEMA
    SOURCE_PREFIX = SOURCE_PREFIX

    source: str
    timestamp_format: str
    scale: dict[str, float]

    def __init__(self, *, source: str, timestamp_format: str, scale: dict[str, float] | None = None):
        self.source = source
        self.timestamp_format = timestamp_format
        self.scale = scale or {}

    def _cast(self, column: str, source_dtype: pl.DataType, target_dtype: pl.DataType) -> pl.Expr:
        expr = pl.col(column)
        if target_dtype == pl.Datetime:
            if source_dtype == pl.String:
                return expr.str.to_datetime(self.timestamp_format, time_zone="UTC", time_unit="us")
            if source_dtype.time_zone is None:
                return expr.dt.replace_time_zone("UTC").dt.cast_time_unit("us")
            return expr.dt.convert_time_zone("UTC").dt.cast_time_unit("us")

        if source_dtype == pl.String and target_dtype.is_integer():
            return expr.str.extract(r"(\d+)").cast(target_dtype)
        return expr.cast(target_dtype)

    @damast.core.describe("Align an AIS source to the canonical AIS schema")
    @damast.core.input({f"{SOURCE_PREFIX}{name}": {} for name in CANONICAL_AIS_SCHEMA})
    @damast.core.output({**CANONICAL_AIS_SCHEMA, "source": {"representation_type": pl.String}},
                        exclusive=True)
    def transform(self, df: AnnotatedDataFrame) -> AnnotatedDataFrame:
        source_schema = df.lazyframe.collect_schema()

        columns = []
        for name, spec in CANONICAL_AIS_SCHEMA.items():
            source_column = self.get_name(f"{SOURCE_PREFIX}{name}")
            expr = self._cast(source_column, source_schema[source_column], spec["representation_type"])
            if name in self.scale:
                expr = expr * self.scale[name]
            columns.append(expr.alias(name))

        df.lazyframe = df.lazyframe.with_columns(*columns, pl.lit(self.source).alias("source"))
        return df
