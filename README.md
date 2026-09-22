# damast-sigspatial2026

This is a replication package for ACM Sigspatial2026 Workshop to illustrate the capabilities and potential of using [damast](https://github.com/simula/damast) for
reproducible data processing pipelines.


## Installation

Install uv
```
$> curl -LsSf https://astral.sh/uv/install.sh | sh

$> uv venv venv-damast
$> source ./venv-damast/bin/activate
```

```
git clone https://github.com/ai4copsec/damast-sigspatial2026
cd damast-sigspatial2026

uv pip install .
```

Ensure that the plugin has successfully been installed and registered:
```
(venv-damast) ➜  damast plugins
damast_sigspatial2026 (damast-sigspatial2026==0.1.1)
    AlignAISSchema          .transformers.align_ais_schema
    AnomalyRatioChart       .transformers.anomaly_ratio_chart
    ConcatDataFrames        .transformers.concat_dataframes
    ExtractGroupStatistics  .transformers.group_statistics
    Healpix                 .transformers.healpix_binning
    HealpixGapMap           .transformers.healpix_gap_map
    ParseTimestamp          .transformers.parse_timestamp
    QuerySuspiciousVessels  .transformers.suspicious_movement
    RegionFilter            .transformers.region_filter
    SuspiciousVesselMap     .transformers.suspicious_vessel_map
    VesselTrajectoryMap     .transformers.vessel_trajectory_map
```

Download and prepare data files for Denmark (aisdk) and US (Marine Cadastre):
```
wget http://aisdata.ais.dk/aisdk-2026-06-01.zip
(venv-damast) ➜  damast convert -f aisdk-2026-06-01.zip --save-as data/aisdk-2026-06-01.parquet

wget https://noaaocm.blob.core.windows.net/ais/csv2/csv2026/ais-2026-06-01.csv.zst
(venv-damast) ➜ damast convert -f ais-2026-06-01.csv.zst --save-as data/ais-2026-06-01.parquet
```

Inspect available data file(s):
```
(venv-damast) ➜ damast inspect -f data/AIS_2026_06_01.parquet
```


## Verification

### Rerun a pregenerated pipeline
Run the pregenerated pipeline(s) to join datasources and process the data further:

Joining datasources:
```
$> damast process --pipeline examples/join_sources.damast.ppl --input-data df=data/aisdk-2026-06-01.parquet --input-data marine-cadastre=data/ais-2026-06-01.parquet --input-data barentswatch=data/AIS_2026_06_01.parquet --output-file results/AIS_2026_06_01-joined.parquet
```

```
$> damast process --pipeline examples/prepare.damast.ppl --input-data ./results/AIS_2026_*-joined.parquet --output-file ./results/AIS_2026.prepare.parquet --base-dir ./results
```

Check the augmented generated dataframe in ./results
```
$> damast inspect -f ./results/AIS_2026.prepare.parquet
```

### Create a pregenerated pipeline

```
$> python src/damast_sigspatial2026/1-prepare.py --output-dir . --pipeline-name prepare export
Saved pipeline: prepare.damast.ppl
```

Run the given pipeline:
```
(venv-damast) ➜  damast process --pipeline prepare.damast.ppl --input-data ./results/AIS_2026_06_01-joined.parquet --output-file results/AIS_2026_06_01.prepared.parquet
Subparser: DataProcessingParser
WARNING:damast.core.transformations:PluginManager: plugin package name 'damast_sigspatial2026' (for '/opt/workspace/damast-sigspatial2026/src/damast_sigspatial2026/transformers') is already importable - skipping
INFO:damast.core.dataframe:Loading parquet: files=['./results/AIS_2026_06_01-joined.parquet']
INFO:damast.core.dataprocessing:#1 validate name=df DataSource (uuid=1ea7614c-fcc0-4c5a-a392-d797de47a78b)
INFO:damast.core.dataprocessing:#2 validate name=drop_missing_timestamp DropMissingOrNan (uuid=d2187c72-18d5-4b19-8e37-07ef0f66983c)
INFO:damast.core.dataprocessing:#3 validate name=filter_ship_types FilterWithin (uuid=863415f8-b64a-4da7-baa6-0780d17db140)
INFO:damast.core.dataprocessing:#4 validate name=delta_time AddDeltaTime (uuid=ae276530-e3f0-4574-a2d6-7836f0622d02)
INFO:damast.core.dataprocessing:#5 validate name=delta_distance DeltaDistance (uuid=20a94897-8aa2-4b4c-9aac-337911d3b661)
INFO:damast.core.dataprocessing:#6 validate name=speed Speed (uuid=4a73d1c9-6bc5-4f5c-baa2-351edff003a0)
INFO:damast.core.dataprocessing:#7 validate name=heading Heading (uuid=08f429a9-533e-4721-b273-e7e1e3849835)
INFO:damast.core.metadata:DataSpecification.merge: using merge strategy other for description: this=true heading (511 = not available) -- other=heading between two locations
INFO:damast.core.metadata:DataSpecification.merge: using merge strategy other for representation_type: this=<class 'int'> -- other=<class 'float'>
INFO:damast.core.metadata:DataSpecification.merge: using merge strategy other for unit: this=deg -- other=rad
INFO:damast.core.dataprocessing:#8 validate name=angular_velocity AngularVelocity (uuid=c0ecbf00-2af1-4ede-a477-a668b0d573dd)
INFO:damast.core.dataprocessing:#9 validate name=cycle_timestamp TimestampCycleTransformer (uuid=4cbd4809-48c6-4884-a1bd-d8060e2f9f94)
INFO:damast.core.dataprocessing:#10 validate name=lat_cycle_transform CycleTransformer (uuid=026d9a97-12d3-4c6b-9fde-14a8d5e22734)
INFO:damast.core.dataprocessing:#11 validate name=lon_cycle_transform CycleTransformer (uuid=8f9de136-5589-4db5-85bb-083691177a9f)
INFO:damast.core.dataprocessing:#12 validate name=healpix Healpix (uuid=40817e99-5cd8-41d0-9d19-53e605ddf66d)
INFO:damast.core.dataprocessing:#13 validate name=group_statistics ExtractGroupStatistics (uuid=5a649da8-7133-4df1-9c5c-482b017c6725)
Step :   0%|                                                                                                     | 0/13 [00:00<?, ?it/s]INFO:damast.core.dataprocessing:#1 run name=df DataSource (uuid=1ea7614c-fcc0-4c5a-a392-d797de47a78b)
INFO:damast.core.dataprocessing:[transform] start: DataSource - {'df': {}}
INFO:damast.core.dataprocessing:[transform] end: DataSource - {'df': {}}: 1.823066 seconds, 30208330 remaining rows)
Step :   8%|███████▏                                                                                     | 1/13 [00:01<00:21,  1.82s/it]INFO:damast.core.dataprocessing:#2 run name=drop_missing_timestamp DropMissingOrNan (uuid=d2187c72-18d5-4b19-8e37-07ef0f66983c)
INFO:damast.core.dataprocessing:[transform] start: DropMissingOrNan - {'df': {'x': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: DropMissingOrNan - {'df': {'x': 'timestamp'}}: 1.102559 seconds, 30208330 remaining rows)
Step :  15%|██████████████▎                                                                              | 2/13 [00:03<00:19,  1.79s/it]INFO:damast.core.dataprocessing:#3 run name=filter_ship_types FilterWithin (uuid=863415f8-b64a-4da7-baa6-0780d17db140)
INFO:damast.core.dataprocessing:[transform] start: FilterWithin - {'df': {'x': 'ship_type'}}
INFO:damast.core.dataprocessing:[transform] end: FilterWithin - {'df': {'x': 'ship_type'}}: 0.37171 seconds, 2663705 remaining rows)
Step :  23%|█████████████████████▍                                                                       | 3/13 [00:04<00:12,  1.22s/it]INFO:damast.core.dataprocessing:#4 run name=delta_time AddDeltaTime (uuid=ae276530-e3f0-4574-a2d6-7836f0622d02)
INFO:damast.core.dataprocessing:[transform] start: AddDeltaTime - {'df': {'group': 'mmsi', 'time_column': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: AddDeltaTime - {'df': {'group': 'mmsi', 'time_column': 'timestamp'}}: 0.384579 seconds, 2663705 remaining rows)
Step :  31%|████████████████████████████▌                                                                | 4/13 [00:05<00:10,  1.15s/it]INFO:damast.core.dataprocessing:#5 run name=delta_distance DeltaDistance (uuid=20a94897-8aa2-4b4c-9aac-337911d3b661)
INFO:damast.core.dataprocessing:[transform] start: DeltaDistance - {'df': {'group': 'mmsi', 'out': 'delta_distance', 'sort': 'timestamp', 'x': 'latitude', 'y': 'longitude'}}
INFO:damast.core.dataprocessing:[transform] end: DeltaDistance - {'df': {'group': 'mmsi', 'out': 'delta_distance', 'sort': 'timestamp', 'x': 'latitude', 'y': 'longitude'}}: 1.421972 seconds, 2656916 remaining rows)
Step :  38%|███████████████████████████████████▊                                                         | 5/13 [00:07<00:12,  1.53s/it]INFO:damast.core.dataprocessing:#6 run name=speed Speed (uuid=4a73d1c9-6bc5-4f5c-baa2-351edff003a0)
INFO:damast.core.dataprocessing:[transform] start: Speed - {'df': {'delta_distance': 'delta_distance', 'delta_time': 'delta_time'}}
INFO:damast.core.dataprocessing:[transform] end: Speed - {'df': {'delta_distance': 'delta_distance', 'delta_time': 'delta_time'}}: 1.48276 seconds, 2656026 remaining rows)
Step :  46%|██████████████████████████████████████████▉                                                  | 6/13 [00:09<00:12,  1.78s/it]INFO:damast.core.dataprocessing:#7 run name=heading Heading (uuid=08f429a9-533e-4721-b273-e7e1e3849835)
INFO:damast.core.dataprocessing:[transform] start: Heading - {'df': {'group': 'mmsi', 'heading': 'heading', 'lat': 'latitude', 'lon': 'longitude', 'sort': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: Heading - {'df': {'group': 'mmsi', 'heading': 'heading', 'lat': 'latitude', 'lon': 'longitude', 'sort': 'timestamp'}}: 1.980605 seconds, 2642656 remaining rows)
Step :  54%|██████████████████████████████████████████████████                                           | 7/13 [00:12<00:12,  2.16s/it]INFO:damast.core.dataprocessing:#8 run name=angular_velocity AngularVelocity (uuid=c0ecbf00-2af1-4ede-a477-a668b0d573dd)
INFO:damast.core.dataprocessing:[transform] start: AngularVelocity - {'df': {'group': 'mmsi', 'heading': 'heading', 'time': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: AngularVelocity - {'df': {'group': 'mmsi', 'heading': 'heading', 'time': 'timestamp'}}: 1.969475 seconds, 2642656 remaining rows)
Step :  62%|█████████████████████████████████████████████████████████▏                                   | 8/13 [00:15<00:12,  2.41s/it]INFO:damast.core.dataprocessing:#9 run name=cycle_timestamp TimestampCycleTransformer (uuid=4cbd4809-48c6-4884-a1bd-d8060e2f9f94)
INFO:damast.core.dataprocessing:[transform] start: TimestampCycleTransformer - {'df': {'x': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: TimestampCycleTransformer - {'df': {'x': 'timestamp'}}: 2.266553 seconds, 2642656 remaining rows)
Step :  69%|████████████████████████████████████████████████████████████████▍                            | 9/13 [00:19<00:11,  2.82s/it]INFO:damast.core.dataprocessing:#10 run name=lat_cycle_transform CycleTransformer (uuid=026d9a97-12d3-4c6b-9fde-14a8d5e22734)
INFO:damast.core.dataprocessing:[transform] start: CycleTransformer - {'df': {'x': 'latitude'}}
INFO:damast.core.dataprocessing:[transform] end: CycleTransformer - {'df': {'x': 'latitude'}}: 2.539094 seconds, 2642656 remaining rows)
Step :  77%|██████████████████████████████████████████████████████████████████████▊                     | 10/13 [00:23<00:09,  3.21s/it]INFO:damast.core.dataprocessing:#11 run name=lon_cycle_transform CycleTransformer (uuid=8f9de136-5589-4db5-85bb-083691177a9f)
INFO:damast.core.dataprocessing:[transform] start: CycleTransformer - {'df': {'x': 'longitude'}}
INFO:damast.core.dataprocessing:[transform] end: CycleTransformer - {'df': {'x': 'longitude'}}: 2.677446 seconds, 2642656 remaining rows)
Step :  85%|█████████████████████████████████████████████████████████████████████████████▊              | 11/13 [00:27<00:07,  3.58s/it]INFO:damast.core.dataprocessing:#12 run name=healpix Healpix (uuid=40817e99-5cd8-41d0-9d19-53e605ddf66d)
INFO:damast.core.dataprocessing:[transform] start: Healpix - {'df': {}}
INFO:damast.core.dataprocessing:[transform] end: Healpix - {'df': {}}: 2.806831 seconds, 2642656 remaining rows)
Step :  92%|████████████████████████████████████████████████████████████████████████████████████▉       | 12/13 [00:32<00:04,  4.03s/it]INFO:damast.core.dataprocessing:#13 run name=group_statistics ExtractGroupStatistics (uuid=5a649da8-7133-4df1-9c5c-482b017c6725)
INFO:damast.core.dataprocessing:[transform] start: ExtractGroupStatistics - {'df': {'delta_time': 'delta_time', 'group': 'mmsi'}}
INFO:damast.core.dataprocessing:[transform] end: ExtractGroupStatistics - {'df': {'delta_time': 'delta_time', 'group': 'mmsi'}}: 8.289574 seconds, 2642656 remaining rows)

Step : 100%|████████████████████████████████████████████████████████████████████████████████████████████| 13/13 [00:41<00:00,  3.16s/it]
shape: (5, 35)
┌───────────┬───────┬─────────┬───────────┬───┬────────────┬─────────────┬─────────────┬────────────┐
│ call_sign ┆ cog   ┆ draught ┆ heading   ┆ … ┆ latitude_y ┆ longitude_x ┆ longitude_y ┆ healpix_id │
│ ---       ┆ ---   ┆ ---     ┆ ---       ┆   ┆ ---        ┆ ---         ┆ ---         ┆ ---        │
│ str       ┆ f64   ┆ f64     ┆ f64       ┆   ┆ f64        ┆ f64         ┆ f64         ┆ i64        │
╞═══════════╪═══════╪═════════╪═══════════╪═══╪════════════╪═════════════╪═════════════╪════════════╡
│ WDF6143   ┆ 316.1 ┆ null    ┆ -2.684937 ┆ … ┆ 0.001084   ┆ 0.001095    ┆ -0.002553   ┆ 50300      │
│ WDF6143   ┆ 316.9 ┆ null    ┆ -2.355565 ┆ … ┆ 0.001032   ┆ 0.001125    ┆ -0.00254    ┆ 50300      │
│ WDF6143   ┆ 311.1 ┆ null    ┆ -1.877337 ┆ … ┆ 0.000976   ┆ 0.001154    ┆ -0.002527   ┆ 50300      │
│ WDF6143   ┆ 311.4 ┆ null    ┆ -2.76293  ┆ … ┆ 0.000959   ┆ 0.001164    ┆ -0.002522   ┆ 50300      │
│ WDF6143   ┆ 319.5 ┆ null    ┆ -2.126268 ┆ … ┆ 0.000912   ┆ 0.001187    ┆ -0.002512   ┆ 50300      │
└───────────┴───────┴─────────┴───────────┴───┴────────────┴─────────────┴─────────────┴────────────┘
shape: (5, 35)
┌───────────┬───────┬─────────┬───────────┬───┬────────────┬─────────────┬─────────────┬────────────┐
│ call_sign ┆ cog   ┆ draught ┆ heading   ┆ … ┆ latitude_y ┆ longitude_x ┆ longitude_y ┆ healpix_id │
│ ---       ┆ ---   ┆ ---     ┆ ---       ┆   ┆ ---        ┆ ---         ┆ ---         ┆ ---        │
│ str       ┆ f64   ┆ f64     ┆ f64       ┆   ┆ f64        ┆ f64         ┆ f64         ┆ i64        │
╞═══════════╪═══════╪═════════╪═══════════╪═══╪════════════╪═════════════╪═════════════╪════════════╡
│ null      ┆ null  ┆ null    ┆ 0.719853  ┆ … ┆ -0.005515  ┆ -0.001506   ┆ -0.002334   ┆ 11710      │
│ null      ┆ 255.1 ┆ null    ┆ -2.889856 ┆ … ┆ -0.005514  ┆ -0.001501   ┆ -0.002338   ┆ 11710      │
│ null      ┆ 226.1 ┆ null    ┆ -0.172386 ┆ … ┆ -0.005517  ┆ -0.001496   ┆ -0.002341   ┆ 11710      │
│ null      ┆ 69.2  ┆ null    ┆ 2.645118  ┆ … ┆ -0.005513  ┆ -0.001502   ┆ -0.002337   ┆ 11710      │
│ null      ┆ null  ┆ null    ┆ 1.775524  ┆ … ┆ -0.005515  ┆ -0.001505   ┆ -0.002334   ┆ 11710      │
└───────────┴───────┴─────────┴───────────┴───┴────────────┴─────────────┴─────────────┴────────────┘
Saved /opt/workspace/damast-sigspatial2026/results/AIS_2026_06_01.prepared.parquet
(venv-damast) ➜  damast-sigspatial2026
```

### Model training

To illustrate a model training for a ForecastTask:
```
KERAS_BACKEND=torch python src/damast_sigspatial2026/2-ml-model-creation.py --input-data ./results/AIS_2026_06_01.prepared.parquet --pipeline ./examples/prepare.damast.ppl
```

After training the artifacts and trained models are available in subfolders of:
```
/tmp/test-output-ais_preparation
```

## License
This project is licensed under the [BSD-3-Clause License](https://github.com/simula/damast/blob/main/LICENSE).
Data (.parquet) published here has been retrieved from [barentswatch](https://www.barentswatch.no/) and is licensed under [Norwegian License for Open Government Data (NLOD) 1.0](https://data.norge.no/nlod/en/1.0).

## Copyright

Copyright (c) 2026 [Simula Research Laboratory, Oslo, Norway](https://www.simula.no/research/research-departments)


## Acknowledgments

The development of damast and this reproduction sample is part of the EU-project [AI4COPSEC](https://ai4copsec.eu) which receives funding
 from the Horizon Europe framework programme under Grant Agreement N. 101190021.
