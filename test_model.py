import sys

import gym
from datetime import datetime
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import CnnPolicy
from stable_baselines import DQN
from agarEnv import AgarEnv


WINDOW_SIZE = (580,580)
IMAGE_SIZE = (120,120)
NUM_FRAMES = 3

env = None

def main(name):
    env = AgarEnv(WINDOW_SIZE, IMAGE_SIZE, NUM_FRAMES,
            max_score=150, visible = 1)

    model = DQN.load(name)

    obs = env.reset()
    while True:
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        if dones:
            obs = env.reset()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("{} <model location>".format(sys.argv[0]))
        sys.exit(0)

    try:
        main(sys.argv[1])
    finally:
        if env is not None:
            env.close()

