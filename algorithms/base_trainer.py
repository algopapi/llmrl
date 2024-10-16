from typing import  Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from accelerate import PartialState

from policies.base_policy import BasePolicy
from common.buffer import Buffer
from common.dataset import EpisodeDataset


@dataclass 
class Checkpoint:
    path: Path
    iteration: int


class TrainerState:
    """
    Keep track of the global trainer state. 
    """
    global_step: int = 0
    epoch: float = 0.0
    iteration: int = 0

    INITIAL_STATE_DICT = {
        "global_step": 0,
        "epoch": 0.0,
        "iteration": 0,
    }

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        self.global_step = state_dict["global_step"]
        self.epoch = state_dict["epoch"]
        self.iteration = state_dict["iteration"]

    def state_dict(self):
        return {
            "global_step": self.global_step,
            "epoch": self.epoch,
            "iteration": self.iteration,
        }

    def __repr__(self):
        return f"TrainerState(global_step={self.global_step}, epoch={self.epoch}, iteration={self.iteration})"


class BaseTrainer(ABC):
    def __init__(
        self,
        project_root_dir: Path,
        distributed_state: PartialState,
        policy: BasePolicy,
        per_device_batch_size: int,
    ):
        """
        Main Trainer object. 

        params:
        policy: BasePolicy,
            The policy to be trained.
        per_device_batch_size: int,
            The batch size per device for training.
        seed: int,
            Random seed for reproducibility.
        path: str = "./trainer_state.pth",
            Path to save and load the trainer state.
        
        """
        self.project_root_dir = project_root_dir
        self._init_trainer_dir()
    
        self.distributed_state = distributed_state

        self.policy = policy
        self.per_device_batch_size = per_device_batch_size
        self.state = TrainerState()

    def _init_trainer_dir(self):
        self.trainer_dir = (self.project_root_dir / "trainer")
        self.trainer_dir.mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def update(self) -> None:
        pass

    def save_trainer_state(self, path: str) -> None:
        raise NotImplementedError("save_trainer_state method is not implemented yet.")

    def load_trainer_state(self, path: str) -> None:
        raise NotImplementedError("load_trainer_state method is not implemented yet.")

class OnPolicyTrainer(BaseTrainer):
    @abstractmethod
    def update(self, episodes: EpisodeDataset) -> None:
        """
            Update method of the on policy trainer, which we will give a list of episodes do to a 
            multi-epoch optimization on. 
        """
        pass

class OffPolicyTrainer(BaseTrainer):
    """
        For Off policy algorithms. 
    """
    @abstractmethod
    def update(self, buffer: Buffer) -> None:
        """
            In the off policy trainer update step we pass in a buffer from which we 
            can sample episodes during a training step. 
        """
        pass