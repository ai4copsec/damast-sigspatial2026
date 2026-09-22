"""
damast plugin transformer: stack two dataframes row-wise - used as the join operator to combine
several (schema-aligned) data sources into one dataframe.
"""
import copy

import damast
import polars as pl
from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import PipelineElement
from damast.core.metadata import MetaData


class ConcatDataFrames(PipelineElement):
    """
    Concatenate 'other' below 'df'. Columns present in only one input are kept and filled with
    null for the rows of the other input; columns present in both must share the same dtype.
    """

    @damast.core.describe("Stack two dataframes row-wise")
    @damast.core.input({})
    @damast.core.input({}, label="other")
    @damast.core.output({})
    def transform(self, df: AnnotatedDataFrame, other: AnnotatedDataFrame) -> AnnotatedDataFrame:
        columns = [copy.deepcopy(spec) for spec in df.metadata.columns]
        columns += [copy.deepcopy(spec) for spec in other.metadata.columns if spec.name not in df.metadata]
        # value ranges/stats were computed per input and do not hold for the combined data
        for spec in columns:
            spec.value_range = None
            spec.value_stats = None

        return AnnotatedDataFrame(
            pl.concat([df.lazyframe, other.lazyframe], how="diagonal"),
            metadata=MetaData(columns=columns, annotations=copy.deepcopy(list(df.metadata.annotations.values()))),
        )
