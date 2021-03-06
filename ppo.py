import gym

from datetime import datetime
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.policies import CnnPolicy
from stable_baselines import PPO2
from agarEnv import AgarEnv


WINDOW_SIZE = (580,580)
IMAGE_SIZE = (120,120)
NUM_FRAMES = 3
EPISODES = 100
MAX_STEPS_LIFE = 200
STEPS = EPISODES*MAX_STEPS_LIFE
logname = 'DQN-' + datetime.now().strftime("%Y:%m:%d--%H:%M:%S") + '-steps:{}'.format(STEPS)

env = None
def main():
    env = AgarEnv(WINDOW_SIZE, IMAGE_SIZE, NUM_FRAMES,
            max_score=150, max_steps_life=MAX_STEPS_LIFE)
    model = PPO2(CnnPolicy, env, verbose = 1, 
            tensorboard_log='logs/')

    model.learn(total_timesteps=STEPS, tb_log_name=logname)
    model.save('models/'+logname)
    
    env.close()

    
if __name__ == "__main__":
    try:
        main()
    finally:
        if env is not None:
            env.close()
