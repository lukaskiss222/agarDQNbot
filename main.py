import gym

from datetime import datetime
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import CnnPolicy
from stable_baselines import DQN
from agarEnv import AgarEnv


WINDOW_SIZE = (580,580)
IMAGE_SIZE = (120,120)
NUM_FRAMES = 7000
STEPS = 
logname = 'DQN-' + datetime.now().strftime("%Y:%m:%d--%H:%M:%S") + '-steps:{}'.format(STEPS)

def main():
    env = AgarEnv(WINDOW_SIZE, IMAGE_SIZE, NUM_FRAMES)
    model = DQN(CnnPolicy, env, verbose = 1, 
            target_network_update_freq=500,
            prioritized_replay=True,
            tensorboard_log='logs/')

    model.learn(total_timesteps=STEPS, tb_log_name=logname)
    model.save('models/'+ logname)


    
if __name__ == "__main__":
    main()
