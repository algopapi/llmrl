from datetime import timedelta

import torch
import hydra
from omegaconf import OmegaConf, dictconfig
from transformers import AutoModelForCausalLM, AutoModel
from accelerate import PartialState

from algorithms.on_policy_algorithm import OnPolicyAlgorithm

from policies.actor_critic_policy import ActorCriticPolicy
from policies.base_critic import PretrainedModelValueHead
from algorithms.ppo.trainer import PPOTrainer
from episode_generators.base_episode_generator import DebugEpisodeGenerator

from runners.base_runner import DistributedRunner

@hydra.main(config_path="../configs", config_name="config", version_base=None)
def test_drunner_ppo_policy(cfg: dictconfig):
    # The policy
    ds_config = cfg.deepspeed
    ds_config = OmegaConf.to_container(ds_config, resolve=True)
    # Wrap this inside a model dir with actor models and critic models definitions?
    # Most likely a good idea. 
    def actor_model_fn():
        ## load gp2 as actor
        return AutoModelForCausalLM.from_pretrained("gpt2")

    def critic_model_fn():
        # Wrap the critic with the value head model.
        critic_backbone = AutoModel.from_pretrained("gpt2")
        return PretrainedModelValueHead(pretrained_model=critic_backbone)

    actor_critic_policy = ActorCriticPolicy
    actor_critic_kwargs = {
        "actor_model_fn": actor_model_fn,
        "critic_model_fn": critic_model_fn,
        "actor_ds_config" : ds_config,
        "critic_ds_config" : ds_config,
    }

    # Train algorithm ( a single update step, multiple epochs)
    ppo_trainer_class = PPOTrainer
    ppo_trainer_kwargs = {
        'per_device_batch_size': 10,
    }

    episode_generator_class = DebugEpisodeGenerator
    episode_generator_kwargs = {
        'file_path': "./test_data/gpt2_imdb_ppo_iter50_samples.json",
        'policy_path': "dummy_gpt2_path.th",
    }
    
    # Define an algorithm (takes a policy and a trainer)
    algorithm_cls = OnPolicyAlgorithm
    algorithm_kwargs = {
        "num_iterations": 1,
        "num_episodes_per_iteration":5,
        "verbose":1,
        "evaluation_freq":10,
        "checkpoint_freq":10  
    }
    
    # The main runner object
    runner = DistributedRunner(
        experiment_name="runner_test",
        directory="experiment",
        use_deepspeed=True,

        policy_cls=actor_critic_policy,
        trainer_cls=ppo_trainer_class,
        episode_generator_cls=episode_generator_class,
        algorithm_cls=algorithm_cls,

        policy_kwargs=actor_critic_kwargs,
        trainer_kwargs=ppo_trainer_kwargs,
        episode_generator_kwargs=episode_generator_kwargs,
        algorithm_kwargs=algorithm_kwargs
    )

    # Start the algorithm
    runner.run()

if __name__ == "__main__":
    test_drunner_ppo_policy()