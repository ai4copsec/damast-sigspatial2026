import shutil
import tempfile
from argparse import ArgumentParser

# The list of modules used for this example
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

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
    ForecastTask,
    ModelInstanceDescription,
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
                 features: List[str],
                 timeline_length: int,
                 output_dir: Path,
                 targets: Optional[List[str]] = None):
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


class BaselineB(Baseline):
    """Placeholder Model to illustrate the use of multiple models"""
    pass


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
    forecast_task = ForecastTask(
        label="forecast-ais-short-sequence",
        pipeline=pipeline, features=features,
        models=[ModelInstanceDescription(BaselineA, {}),
                ModelInstanceDescription(BaselineB, {}),
                ],
        group_column="mmsi",
        sequence_length=5,
        forecast_length=1,
        training_parameters=TrainingParameters(epochs=1,
                                               validation_steps=1)
    )

    experiment = Experiment(learning_task=forecast_task,
                            input_data=args.input_data,
                            output_directory=tmp_path)

    report = experiment.run()
    with open(report, "r") as f:
        print(f.read())
