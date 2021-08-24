from abc import abstractmethod
from typing import Dict, List, Optional, Union

import optuna
import torch
from flash.core.data.data_module import DataModule

from gradsflow.automodel.automodel import AutoModel

# noinspection PyTypeChecker
from gradsflow.utility.common import listify


class AutoClassifier(AutoModel):
    """Base Class for Auto Classification Hyperparameter search"""

    DEFAULT_BACKBONES = []

    def __init__(
        self,
        datamodule: DataModule,
        max_epochs: int = 10,
        n_trials: int = 100,
        optimization_metric: Optional[str] = None,
        suggested_backbones: Union[List, str, None] = None,
        suggested_conf: Optional[dict] = None,
        timeout: int = 600,
        prune: bool = True,
        optuna_confs: Optional[Dict] = None,
    ):
        super().__init__(
            datamodule,
            max_epochs=max_epochs,
            optimization_metric=optimization_metric,
            n_trials=n_trials,
            suggested_conf=suggested_conf,
            timeout=timeout,
            prune=prune,
            optuna_confs=optuna_confs,
        )

        if isinstance(suggested_backbones, (str, list, tuple)):
            self.suggested_backbones = listify(suggested_backbones)
        elif suggested_backbones is None:
            self.suggested_backbones = self.DEFAULT_BACKBONES
        else:
            raise UserWarning("Invalid suggested_backbone type!")

        self.datamodule = datamodule
        self.num_classes = datamodule.num_classes

    def forward(self, x):
        if not self.model:
            raise UserWarning("model not initialized yet!")
        return self.model(x)

    # noinspection PyTypeChecker
    def _get_trial_hparams(self, trial: optuna.Trial) -> Dict[str, str]:
        """Fetch hyperparameters from current optuna.Trial and returns
        key-value pair of hparams"""

        trial_backbone = trial.suggest_categorical("backbone", self.suggested_backbones)
        trial_lr = trial.suggest_float("lr", *self.suggested_lr, log=True)
        trial_optimizer = trial.suggest_categorical(
            "optimizer", self.suggested_optimizers
        )
        hparams = {
            "backbone": trial_backbone,
            "lr": trial_lr,
            "optimizer": trial_optimizer,
        }
        return hparams

    @abstractmethod
    def build_model(self, **kwargs) -> torch.nn.Module:
        raise NotImplementedError
