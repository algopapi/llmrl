from abc import ABC, abstractmethod
from pathlib import Path

from logging import Logger

from deepspeed import DeepSpeedEngine

from policy.base_policy import BasePolicy 
from episode_generation.base_episode_generator import BaseEpisodeGenerator
from algorithms.base_trainer import BaseTrainer



class BaseAlgorithm(ABC):
    _logger: Logger 
    def __init__(
            self, 
            policy: BasePolicy, 
            trainer: BaseTrainer,
            episode_generator: BaseEpisodeGenerator, 
            verbose: int = 0,
            num_iterations: int = 100,
            num_episodes_per_iteration: int = 100,
            evaluation_freq: int = 10,
            checkpoint_freq: int = 10,
    ):
        """
            Base of Reinforcement Learning Algorithms.

            :param policy: The policy to use (PPO, ARCHER, etc)
            :param trainer: The trainer to use. ( Here we write the update rule and such)
            :param episode_generator: Returns episodes to train on. 

            :param device: The device to use.
            :param verbose: The verbosity level.
        """

        self.policy = policy
        self.trainer = trainer
        self.episode_generator = episode_generator
        self.verbose = verbose
        self.num_iterations = num_iterations
        self.num_episodes_per_iteration = num_episodes_per_iteration
        self.evaluation_freq = evaluation_freq
        self.checkpoint_freq = checkpoint_freq
    
    def set_root_dir(self, path: Path):
        self.experiment_root_dir = path

    
    def set_deepspeed(self, distirbuted_state: DeepSpeedEngine):
        self.distributed_state = distirbuted_state


    @abstractmethod
    def learn(self, *args, **kwargs) -> None:
        raise NotImplementedError("learn method is not implemented yet.")

    @property
    def logger(self) -> Logger:
        raise NotImplementedError("logger method is not implemented yet.")