import gym

from datetime import datetime
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import LnCnnPolicy
from stable_baselines import DQN
from agarEnv import AgarEnv


WINDOW_SIZE = (580,580)
IMAGE_SIZE = (120,120)
NUM_FRAMES = 3
EPISODES = 170
MAX_STEPS_LIFE = 200
STEPS = EPISODES*MAX_STEPS_LIFE
logname = 'DQN-' + datetime.now().strftime("%Y:%m:%d--%H:%M:%S") + '-steps:{}'.format(STEPS)

env = None
def main():
    env = AgarEnv(WINDOW_SIZE, IMAGE_SIZE, NUM_FRAMES,
            max_score=150, max_steps_life=MAX_STEPS_LIFE)
    model = DQN(LnCnnPolicy, env, verbose = 1, 
            target_network_update_freq=2000,
            prioritized_replay=True,
            learning_rate=0.00025,
            batch_size=64,
            #buffer_size=100000, #I run our of memory with 16GB RAM :D
            buffer_size=25000,
            param_noise=True,
            exploration_fraction=0.25, 
            exploration_final_eps=0.1,
            learning_starts=1000,
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
