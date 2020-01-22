import gym
from gym import spaces
from EnviromentAgar import EnviromentAgar
from rewards import SimpleRewards
import numpy as np
import copy

class AgarEnv(gym.Env):


    metadata = {'render.modes': ['human']}

    def __init__(self, windows_size, image_size, 
            num_frames, max_steps_life = 200,
            max_score = 50):
        super(AgarEnv, self).__init__()

        self.stand = 0
        self.render_images = []

        self.image_size = image_size
        self.windows_size = windows_size
        self.num_frames = num_frames

        self.max_steps_life = max_steps_life
        self.max_score = max_score
        
        self.lived = 0
        self.buffer = None
        self.last_reward = None

        self.observation_space = spaces.Box(low = 0,
                high=255,
                shape=(image_size[0], image_size[1], num_frames),
                dtype=np.uint8)
        self.action_space = spaces.Discrete(9)
        self.envAgar = EnviromentAgar(*windows_size, 
                image_size = image_size)
        
    
        #We create our rewrds calculator
        self.critic = SimpleRewards(self.max_steps_life, self.max_score)

    def step(self, action):
        if action == 4:
            self.stand+=1
        else:
            self.stand = 0

        if self.stand == 40:
            print("To long standing!!!!!!!!!")

        info = {}
        if self.buffer is None:
            raise EnvironmentError('First run reset function')
        self.lived+=1
        done = False
        temp_scores = []
        
        done_reward = self.critic.calculateReward(self.envAgar.getScore(),
                True)
        if self.lived >= self.max_steps_life:
            return self.buffer, done_reward, True, info
        if self.critic.max >= self.max_score:
            return self.buffer, done_reward, True, info

        self.buffer = [] # reset buffer for images
        self.render_images = []
        for i in range(self.num_frames):
            st, score, temp_done = self.envAgar.step(action)
            if score >= self.max_score:
                done = True

            self.buffer.append(st)
            done = done | temp_done
            temp_scores.append(score)


        self._stackImages()
        self.last_reward = self.critic.calculateReward(max(temp_scores), done)
        
        return self.buffer, self.last_reward, done, info 
            

    def reset(self):
        st = self.envAgar.reset()
        self.buffer = [st]*self.num_frames
        self._stackImages()
        self.last_reward = self.envAgar.getScore()
        self.lived = 0

        #We also reset our Critic
        self.critic.reset(self.last_reward)
        return self.buffer

    def render(self, mode='human', close=False):
        
        pass

    def close(self):
        self.envAgar.close()

    def _stackImages(self):
        self.buffer = np.array(self.buffer)
        self.buffer = np.moveaxis(self.buffer, 0,2)

if __name__ == "__main__":
    env = AgarEnv()
    obs = env.reset()
    obs, rewards, done, info = env.step(action)

