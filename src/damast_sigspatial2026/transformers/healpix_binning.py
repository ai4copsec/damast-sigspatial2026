"""
damast plugin transformer: bin lat/lon positions into HEALPix pixel ids.

This file is not part of the damast package - it is picked up as a local plugin via the
DAMAST_PLUGIN_PATH mechanism (see damast.core.transformations.PluginManager), which makes
'Healpix' resolvable by module_name='healpix_binning' both when building the pipeline and when
it is later replayed with `damast process`.

Note: this plugin module is deliberately not named 'healpix.py' - the PluginManager registers
loaded plugin files in sys.modules under their filename stem, which would otherwise shadow the
real 'healpix' package that this file imports below.
"""
import damast
import healpix as hp
import polars as pl
from damast.core.dataframe import AnnotatedDataFrame
from damast.core.dataprocessing import PipelineElement


class Healpix(PipelineElement):
    """
    Add a HEALPix pixel id (nested scheme) for each lat/lon position.
    """

    nside: int

    def __init__(self, *, nside: int = 128):
        self.nside = nside

    @damast.core.describe("Add healpix id")
    @damast.core.input({
        "latitude": {"representation_type": float, "unit": "deg"},
        "longitude": {"representation_type": float, "unit": "deg"},
    })
    @damast.core.output({"healpix_id": {"representation_type": int, "description": "Healpix location"}})
    def transform(self, df: AnnotatedDataFrame) -> AnnotatedDataFrame:
        latitude = self.get_name("latitude")
        longitude = self.get_name("longitude")

        df.lazyframe = df.lazyframe.with_columns(
            healpix_id=pl.struct([latitude, longitude]).map_batches(
                # https://github.com/healpy/healpy/issues/602
                lambda s: hp.ang2pix(
                    nside=self.nside,
                    theta=s.struct.field(longitude),
                    phi=s.struct.field(latitude),
                    lonlat=True,
                ),
                return_dtype=int,
            )
        )
        return df
