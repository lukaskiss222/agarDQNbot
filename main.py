import time
import numpy as np
import random
import EnviromentAgar as EA
import grabimage as gi

from datetime import datetime
from DeepQModel import DeepQModel
from rewards import CombinedRewards
from selenium import webdriver
from tensor_board_logger import TensorBoardLogger



TOP_BAR = 74
BROWSER_WIDTH = 580
BROWSER_HIGHT = 580 + TOP_BAR
SCREENSHOT_MONITOR = {'top': 250, 'left': 0, 'width': BROWSER_WIDTH*2, 'height': (BROWSER_HIGHT - TOP_BAR)*2}

SETTINGS_NAME = {"set": ["showSkins", "darkTheme", "showGrid" ,"showBorder"],
                "unset": ["showNames", "showColor", "showMass",
                        "showChat", "showMinimap", "showPosition", "moreZoom",
                        "fillSkin", "backgroundSectors", "jellyPhysics", "playSounds"]}

TOT_FRAME = 3000000
TOT_SCORE = 200
MIN_OBSERVATION = 500
NUM_ACTIONS = 9
NUM_FRAMES = 3



if __name__ == "__main__":
    a = EA.EnviromentAgar(580,580, botsNumber=50)
    agent = DeepQModel(NUM_ACTIONS,NUM_FRAMES)
    observation_num = 0
    # number of deads
    step = 0

    
    rewardO = CombinedRewards(TOT_FRAME, TOT_SCORE)
    logdir = "logs/" + datetime.now().strftime("%Y%m%d-%H%M%S")

    logger = TensorBoardLogger(logdir)
    

    while observation_num < TOT_FRAME:
        
        
        first = a.reset()/255
        rewardO.reset(a.getScore())
        print("Initial score: ", a.getScore())
        state = np.array([first]*NUM_FRAMES)
        state = np.moveaxis(state,0,NUM_FRAMES - 1)

        done = False
        loss = 0
        
        while not done:
            action = agent.act(state)
            buffer = []
            temp_rewards = []
            reward = 0

            

            for i in range(NUM_FRAMES):
                
                im, temp_reward, temp_done = a.step(action)
                if im is not None:
                    im = im/255

                else:
                    # We will not use it anyway, so we create random image
                    #for batch calculation of our network
                    im = np.random.rand(*agent.model.input_shape[1:3])
                buffer.append(im)
                done = done | temp_done
                temp_rewards.append(temp_reward)

            
            reward = rewardO.calculateReward(max(temp_rewards),done)

            next_state = np.array(buffer)
            next_state = np.moveaxis(next_state, 0, NUM_FRAMES - 1)


            sample = state, action, reward, next_state, done
            agent.remember(sample)

            state = next_state

            if observation_num > MIN_OBSERVATION:
                loss = agent.replay()


            if done:
                print("Lived with maximum time ", rewardO.count_calls)
                print("Earned a total of reward equal to ", rewardO.calculateTotalReward())
                logger.log_scalar("lived",rewardO.count_calls,step)
                logger.log_scalar("rewards", rewardO.calculateTotalReward(), step)
                
                
                loss_buf = []
                step+=1
                
        

            observation_num+=1
            logger.log_scalar("epsilon", agent.epsilon, observation_num)
            logger.log_scalar("AVG-loss", loss, observation_num)


    a.close()
