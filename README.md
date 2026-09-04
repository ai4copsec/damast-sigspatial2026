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
Healpix: damast_sigspatial2026.transformers.healpix_binning:Healpix
ParseTimestamp: damast_sigspatial2026.transformers.parse_timestamp:ParseTimestamp
```

Check the data file:
```
(venv-damast) ➜ damast inspect -f data/AIS_2026_06_01.parquet
```


## Verification

### Rerun an pregenerated pipeline
Run the pregenerated pipeline (example-pipeline.damast.ppl):

```
$> damast process --pipeline examples/prepare.damast.ppl --input-data ./data/AIS_2026_*.parquet --output-file ./results/AIS_2026.prepare.parquet 
```

Check the augmented generated dataframe in ./results
```
$> damast inspect -f ./results/AIS_2026.prepare.parquet
```

### Create a pregenerated pipeline

```
$> python src/damast_sigspatial2026/0-prepare.py --output-dir . --pipeline-name prepare export
Saved pipeline: prepare.damast.ppl
```

Run the given pipeline:
```
(venv-damast) ➜  damast-sigspatial2026 damast process --pipeline prepare.damast.ppl --input-data ./data/AIS_2026_06_01.parquet --output-file results/AIS_2026_06_01.prepared.parquet
Subparser: DataProcessingParser
INFO:damast.core.dataframe:Loading parquet: files=['./data/AIS_2026_06_01.parquet']
INFO:damast.core.dataprocessing:#1 validate name=df DataSource (uuid=bd6a6850-9513-4ed5-ac01-a2b1f4107ddf)
INFO:damast.core.dataprocessing:#2 validate name=parse_timestamp ParseTimestamp (uuid=92a980c5-0571-4832-bb79-a9fc07cd3362)
INFO:damast.core.dataprocessing:#3 validate name=filter_ship_types FilterWithin (uuid=4b344174-f9bc-4069-945c-59ad820eb7fe)
INFO:damast.core.dataprocessing:#4 validate name=delta_time AddDeltaTime (uuid=cec14d5c-d6c7-4090-bb1f-7e20dd659c43)
INFO:damast.core.dataprocessing:#5 validate name=delta_distance DeltaDistance (uuid=900ef590-00fa-4f77-b7ad-ec0b58e23974)
INFO:damast.core.dataprocessing:#6 validate name=speed Speed (uuid=68a701f6-5758-4645-834e-cc42b4213781)
INFO:damast.core.dataprocessing:#7 validate name=heading Heading (uuid=9c601f2e-86a5-4ca9-b8e8-031d7dc7e55f)
INFO:damast.core.dataprocessing:#8 validate name=angular_velocity AngularVelocity (uuid=7ae392d1-a25a-4e7b-8e59-27c7edfcd011)
INFO:damast.core.dataprocessing:#9 validate name=cycle_timestamp TimestampCycleTransformer (uuid=e4d77b98-d3f4-4953-901e-6a750e7aba58)
INFO:damast.core.dataprocessing:#10 validate name=lat_cycle_transform CycleTransformer (uuid=74ec510e-8ff4-4dc1-8c15-414bfe8de342)
INFO:damast.core.dataprocessing:#11 validate name=lon_cycle_transform CycleTransformer (uuid=d0d78407-a150-439c-8104-4759e0ef45ab)
INFO:damast.core.dataprocessing:#12 validate name=healpix Healpix (uuid=19ded1c9-fcab-4412-9c8b-828f9be76e59)
Step :   0%|                                                                                                                                                                                                                                    | 0/12 [00:00<?, ?it/s]INFO:damast.core.dataprocessing:#1 run name=df DataSource (uuid=bd6a6850-9513-4ed5-ac01-a2b1f4107ddf)
INFO:damast.core.dataprocessing:[transform] start: DataSource - {'df': {}}
INFO:damast.core.dataprocessing:[transform] end: DataSource - {'df': {}}: 0.135365 seconds, 2880055 remaining rows)
Step :   8%|██████████████████▎                                                                                                                                                                                                         | 1/12 [00:00<00:01,  7.37it/s]INFO:damast.core.dataprocessing:#2 run name=parse_timestamp ParseTimestamp (uuid=92a980c5-0571-4832-bb79-a9fc07cd3362)
INFO:damast.core.dataprocessing:[transform] start: ParseTimestamp - {'df': {'from': 'msgtime', 'to': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: ParseTimestamp - {'df': {'from': 'msgtime', 'to': 'timestamp'}}: 0.001887 seconds, 2880055 remaining rows)
Step :  17%|████████████████████████████████████▋                                                                                                                                                                                       | 2/12 [00:00<00:01,  5.76it/s]INFO:damast.core.dataprocessing:#3 run name=filter_ship_types FilterWithin (uuid=4b344174-f9bc-4069-945c-59ad820eb7fe)
INFO:damast.core.dataprocessing:[transform] start: FilterWithin - {'df': {'x': 'shipType'}}
INFO:damast.core.dataprocessing:[transform] end: FilterWithin - {'df': {'x': 'shipType'}}: 0.001725 seconds, 1568282 remaining rows)
Step :  25%|███████████████████████████████████████████████████████                                                                                                                                                                     | 3/12 [00:00<00:01,  5.90it/s]INFO:damast.core.dataprocessing:#4 run name=delta_time AddDeltaTime (uuid=cec14d5c-d6c7-4090-bb1f-7e20dd659c43)
INFO:damast.core.dataprocessing:[transform] start: AddDeltaTime - {'df': {'group': 'mmsi', 'time_column': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: AddDeltaTime - {'df': {'group': 'mmsi', 'time_column': 'timestamp'}}: 0.001771 seconds, 1568282 remaining rows)
Step :  33%|█████████████████████████████████████████████████████████████████████████▎                                                                                                                                                  | 4/12 [00:00<00:02,  3.56it/s]INFO:damast.core.dataprocessing:#5 run name=delta_distance DeltaDistance (uuid=900ef590-00fa-4f77-b7ad-ec0b58e23974)
INFO:damast.core.dataprocessing:[transform] start: DeltaDistance - {'df': {'group': 'mmsi', 'out': 'delta_distance', 'sort': 'timestamp', 'x': 'latitude', 'y': 'longitude'}}
INFO:damast.core.dataprocessing:[transform] end: DeltaDistance - {'df': {'group': 'mmsi', 'out': 'delta_distance', 'sort': 'timestamp', 'x': 'latitude', 'y': 'longitude'}}: 0.00395 seconds, 1566163 remaining rows)
Step :  42%|███████████████████████████████████████████████████████████████████████████████████████████▋                                                                                                                                | 5/12 [00:01<00:02,  2.89it/s]INFO:damast.core.dataprocessing:#6 run name=speed Speed (uuid=68a701f6-5758-4645-834e-cc42b4213781)
INFO:damast.core.dataprocessing:[transform] start: Speed - {'df': {'delta_distance': 'delta_distance', 'delta_time': 'delta_time'}}
INFO:damast.core.dataprocessing:[transform] end: Speed - {'df': {'delta_distance': 'delta_distance', 'delta_time': 'delta_time'}}: 0.002103 seconds, 1564730 remaining rows)
Step :  50%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████                                                                                                              | 6/12 [00:01<00:02,  2.67it/s]INFO:damast.core.dataprocessing:#7 run name=heading Heading (uuid=9c601f2e-86a5-4ca9-b8e8-031d7dc7e55f)
INFO:damast.core.dataprocessing:[transform] start: Heading - {'df': {'group': 'mmsi', 'heading': 'heading', 'lat': 'latitude', 'lon': 'longitude', 'sort': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: Heading - {'df': {'group': 'mmsi', 'heading': 'heading', 'lat': 'latitude', 'lon': 'longitude', 'sort': 'timestamp'}}: 0.003235 seconds, 1560530 remaining rows)
Step :  58%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▎                                                                                           | 7/12 [00:02<00:02,  2.33it/s]INFO:damast.core.dataprocessing:#8 run name=angular_velocity AngularVelocity (uuid=7ae392d1-a25a-4e7b-8e59-27c7edfcd011)
INFO:damast.core.dataprocessing:[transform] start: AngularVelocity - {'df': {'group': 'mmsi', 'heading': 'heading', 'time': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: AngularVelocity - {'df': {'group': 'mmsi', 'heading': 'heading', 'time': 'timestamp'}}: 0.002479 seconds, 1560530 remaining rows)
Step :  67%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▋                                                                         | 8/12 [00:02<00:01,  2.08it/s]INFO:damast.core.dataprocessing:#9 run name=cycle_timestamp TimestampCycleTransformer (uuid=e4d77b98-d3f4-4953-901e-6a750e7aba58)
INFO:damast.core.dataprocessing:[transform] start: TimestampCycleTransformer - {'df': {'x': 'timestamp'}}
INFO:damast.core.dataprocessing:[transform] end: TimestampCycleTransformer - {'df': {'x': 'timestamp'}}: 2.035472 seconds, 1560530 remaining rows)
Step :  75%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                                                       | 9/12 [00:05<00:03,  1.22s/it]INFO:damast.core.dataprocessing:#10 run name=lat_cycle_transform CycleTransformer (uuid=74ec510e-8ff4-4dc1-8c15-414bfe8de342)
INFO:damast.core.dataprocessing:[transform] start: CycleTransformer - {'df': {'x': 'latitude'}}
INFO:damast.core.dataprocessing:[transform] end: CycleTransformer - {'df': {'x': 'latitude'}}: 2.471535 seconds, 1560530 remaining rows)
Step :  83%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▌                                    | 10/12 [00:09<00:03,  1.85s/it]INFO:damast.core.dataprocessing:#11 run name=lon_cycle_transform CycleTransformer (uuid=d0d78407-a150-439c-8104-4759e0ef45ab)
INFO:damast.core.dataprocessing:[transform] start: CycleTransformer - {'df': {'x': 'longitude'}}
INFO:damast.core.dataprocessing:[transform] end: CycleTransformer - {'df': {'x': 'longitude'}}: 3.04514 seconds, 1560530 remaining rows)
Step :  92%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▊                  | 11/12 [00:13<00:02,  2.51s/it]INFO:damast.core.dataprocessing:#12 run name=healpix Healpix (uuid=19ded1c9-fcab-4412-9c8b-828f9be76e59)
INFO:damast.core.dataprocessing:[transform] start: Healpix - {'df': {}}
INFO:damast.core.dataprocessing:[transform] end: Healpix - {'df': {}}: 3.58126 seconds, 1560530 remaining rows)
Step : 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 12/12 [00:18<00:00,  1.50s/it]
shape: (5, 47)
┌──────────┬──────────┬──────────────────┬─────────────┬───┬────────────┬─────────────┬─────────────┬────────────┐
│ altitude ┆ callSign ┆ courseOverGround ┆ destination ┆ … ┆ latitude_y ┆ longitude_x ┆ longitude_y ┆ healpix_id │
│ ---      ┆ ---      ┆ ---              ┆ ---         ┆   ┆ ---        ┆ ---         ┆ ---         ┆ ---        │
│ i64      ┆ str      ┆ f64              ┆ str         ┆   ┆ f64        ┆ f64         ┆ f64         ┆ i64        │
╞══════════╪══════════╪══════════════════╪═════════════╪═══╪════════════╪═════════════╪═════════════╪════════════╡
│ null     ┆ ONJY     ┆ 358.5            ┆ BEANR>NOMON ┆ … ┆ -0.001349  ┆ 0.002586    ┆ 0.001015    ┆ 12643      │
│ null     ┆ ONJY     ┆ 357.4            ┆ BEANR>NOMON ┆ … ┆ -0.001491  ┆ 0.002584    ┆ 0.00102     ┆ 12643      │
│ null     ┆ ONJY     ┆ 357.3            ┆ BEANR>NOMON ┆ … ┆ -0.001638  ┆ 0.002581    ┆ 0.001028    ┆ 12643      │
│ null     ┆ ONJY     ┆ 357.5            ┆ BEANR>NOMON ┆ … ┆ -0.001736  ┆ 0.002579    ┆ 0.001033    ┆ 12643      │
│ null     ┆ ONJY     ┆ 358.6            ┆ BEANR>NOMON ┆ … ┆ -0.001879  ┆ 0.002577    ┆ 0.001037    ┆ 12643      │
└──────────┴──────────┴──────────────────┴─────────────┴───┴────────────┴─────────────┴─────────────┴────────────┘
shape: (5, 47)
┌──────────┬──────────┬──────────────────┬─────────────┬───┬────────────┬─────────────┬─────────────┬────────────┐
│ altitude ┆ callSign ┆ courseOverGround ┆ destination ┆ … ┆ latitude_y ┆ longitude_x ┆ longitude_y ┆ healpix_id │
│ ---      ┆ ---      ┆ ---              ┆ ---         ┆   ┆ ---        ┆ ---         ┆ ---         ┆ ---        │
│ i64      ┆ str      ┆ f64              ┆ str         ┆   ┆ f64        ┆ f64         ┆ f64         ┆ i64        │
╞══════════╪══════════╪══════════════════╪═════════════╪═══╪════════════╪═════════════╪═════════════╪════════════╡
│ null     ┆ C6IF6    ┆ null             ┆ null        ┆ … ┆ -0.004351  ┆ -0.002603   ┆ -0.00097    ┆ 1628       │
│ null     ┆ C6IF6    ┆ null             ┆ null        ┆ … ┆ -0.004348  ┆ -0.002594   ┆ -0.000993   ┆ 1628       │
│ null     ┆ C6IF6    ┆ 282.2            ┆ null        ┆ … ┆ -0.004357  ┆ -0.002452   ┆ -0.001306   ┆ 1515       │
│ null     ┆ C6IF6    ┆ null             ┆ null        ┆ … ┆ -0.00435   ┆ -0.002597   ┆ -0.000986   ┆ 1628       │
│ null     ┆ C6IF6    ┆ null             ┆ null        ┆ … ┆ -0.00434   ┆ -0.002245   ┆ -0.001636   ┆ 1515       │
└──────────┴──────────┴──────────────────┴─────────────┴───┴────────────┴─────────────┴─────────────┴────────────┘
Saved /workspace/damast-sigspatial2026/results/AIS_2026_06_01.prepared.parquet
(venv-damast) ➜  damast-sigspatial2026
```




