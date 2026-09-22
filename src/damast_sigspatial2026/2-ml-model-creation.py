import shutil
import tempfile
from argparse import ArgumentParser

# The list of modules used for this example
from collections import OrderedDict
from pathlib import Path

# The current development has focused on a keras-based Machine Learning setup
# export KERAS_BACKEND=torch
# to set the backend to pytorch
import keras

# Data processing is centered around a DataProcessingPipeline which consists of multiple PipelineElement being run
# in sequence
from damast.core.dataprocessing import DataProcessingPipeline

# The experiment setup
from damast.ml.experiments import (
    Experiment,
    ModelInstanceDescription,
    TemporalForecastTask,
    TrainingParameters,
)

# To allow the machine learning process to be simplified, we offer a 'BaseModel' that should be inherited from
from damast.ml.models.base import BaseModel


# For performance reasons the underlying data handling library is 'polars'
class Baseline(BaseModel):
    """
    This is a placeholder ML model that illustrates the minimal
    requirements.
    """
    input_specs = OrderedDict({
        "lat_x": {"length": 1},
        "lat_y": {"length": 1},
        "lon_x": {"length": 1},
        "lon_y": {"length": 1}
    })

    output_specs = OrderedDict({
        "lat_x": {"length": 1},
        "lat_y": {"length": 1},
        "lon_x": {"length": 1},
        "lon_y": {"length": 1}
    })

    def __init__(self,
                 name: str,
                 features: list[str],
                 timeline_length: int,
                 output_dir: Path,
                 targets: list[str] | None = None):
        self.timeline_length = timeline_length

        super().__init__(name=name,
                         output_dir=output_dir,
                         features=features,
                         targets=targets)

    def _init_model(self):
        features_width = len(self.features)
        targets_width = len(self.targets)

        self.model = keras.models.Sequential([
            keras.layers.Flatten(input_shape=[self.timeline_length, features_width]),
            keras.layers.Dense(targets_width)
        ])


class BaselineA(Baseline):
    """Placeholder Model to illustrate the use of multiple models"""
    pass


@keras.saving.register_keras_serializable(package="damast_sigspatial2026")
class PositionEmbedding(keras.layers.Layer):
    """Add a learned embedding per sequence position, so attention can tell the time steps apart."""

    def build(self, input_shape):
        self.position_embedding = self.add_weight(shape=(input_shape[1], input_shape[2]),
                                                  initializer="random_normal",
                                                  name="position_embedding")

    def call(self, x):
        return x + self.position_embedding


class BaselineTransformer(Baseline):
    """
    Transformer encoder: projects each time step to `embed_dim`, adds a position embedding and
    applies `num_layers` blocks of self-attention plus feed-forward (each with residual connection
    and layer normalization), then pools over time to predict the targets.
    """

    def __init__(self,
                 name: str,
                 features: list[str],
                 timeline_length: int,
                 output_dir: Path,
                 targets: list[str] | None = None,
                 embed_dim: int = 32,
                 num_heads: int = 4,
                 ff_dim: int = 64,
                 num_layers: int = 2,
                 dropout: float = 0.1):
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.num_layers = num_layers
        self.dropout = dropout

        super().__init__(name=name,
                         features=features,
                         timeline_length=timeline_length,
                         output_dir=output_dir,
                         targets=targets)

    def _init_model(self):
        inputs = keras.Input(shape=(self.timeline_length, len(self.features)))
        x = PositionEmbedding()(keras.layers.Dense(self.embed_dim)(inputs))

        for _ in range(self.num_layers):
            attention = keras.layers.MultiHeadAttention(num_heads=self.num_heads,
                                                        key_dim=self.embed_dim // self.num_heads,
                                                        dropout=self.dropout)(x, x)
            x = keras.layers.LayerNormalization()(x + attention)

            feed_forward = keras.layers.Dense(self.ff_dim, activation="relu")(x)
            feed_forward = keras.layers.Dropout(self.dropout)(keras.layers.Dense(self.embed_dim)(feed_forward))
            x = keras.layers.LayerNormalization()(x + feed_forward)

        x = keras.layers.GlobalAveragePooling1D()(x)
        outputs = keras.layers.Dense(len(self.targets))(x)

        self.model = keras.Model(inputs=inputs, outputs=outputs, name=self.name)


class BaselineLSTM(Baseline):
    """
    Recurrent model: `num_layers` stacked LSTM layers of `units` cells each, the last one's final
    hidden state is mapped to the targets.
    """

    def __init__(self,
                 name: str,
                 features: list[str],
                 timeline_length: int,
                 output_dir: Path,
                 targets: list[str] | None = None,
                 units: int = 32,
                 num_layers: int = 2,
                 dropout: float = 0.1):
        self.units = units
        self.num_layers = num_layers
        self.dropout = dropout

        super().__init__(name=name,
                         features=features,
                         timeline_length=timeline_length,
                         output_dir=output_dir,
                         targets=targets)

    def _init_model(self):
        inputs = keras.Input(shape=(self.timeline_length, len(self.features)))
        x = inputs
        for layer in range(self.num_layers):
            # all but the last layer pass on the full sequence to the next LSTM layer
            x = keras.layers.LSTM(self.units,
                                  dropout=self.dropout,
                                  return_sequences=layer < self.num_layers - 1)(x)
        outputs = keras.layers.Dense(len(self.targets))(x)

        self.model = keras.Model(inputs=inputs, outputs=outputs, name=self.name)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--pipeline", type=str, help="Path to pipeline (*.damast.ppl)")
    parser.add_argument("--input-data", nargs='+', type=str, help="Datafiles to use for training")

    args, unknown_options = parser.parse_known_args()


    tmp_path = Path(tempfile.gettempdir()) / "test-output-ais_preparation"
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True)

    pipeline = DataProcessingPipeline.load(args.pipeline)

    features = ["latitude_x", "latitude_y", "longitude_x", "longitude_y"]
    forecast_task = TemporalForecastTask(
        label="forecast-ais-short-sequence",
        pipeline=pipeline, features=features,
        models=[ModelInstanceDescription(BaselineA, {}),
                ModelInstanceDescription(BaselineTransformer, {}),
                ModelInstanceDescription(BaselineLSTM, {}),
                ],
        group_column="mmsi",
        timestamp_column="timestamp",
        sequence_length=5,
        window="30m",
        forecast_horizon="5m",
        forecast_length=1,
        max_gap="5m",
        training_parameters=TrainingParameters(epochs=100,
                                               validation_steps=20)
    )

    experiment = Experiment(learning_task=forecast_task,
                            input_data=args.input_data,
                            output_directory=tmp_path)

    report = experiment.run()
    with open(report, "r") as f:
        print(f.read())
