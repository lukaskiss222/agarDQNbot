import time
import numpy as np
import random
import EnviromentAgar as EA
import grabimage as gi

from datetime import datetime
from DeepQModel import DeepQModel
from rewards import SimpleRewards
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
TOT_SCORE = 50
TOT_FRAMES_IN_LEVEL = 150
MIN_OBSERVATION = 500
NUM_ACTIONS = 9
NUM_FRAMES = 3
SAVE_FRAMES = 1000





if __name__ == "__main__":
    a = EA.EnviromentAgar(580,580, botsNumber=0)
    agent = DeepQModel(NUM_ACTIONS,NUM_FRAMES, intEpsilon=0.9, 
            epislon_decay=80000, TAU=10000, lr=0.00025)
    observation_num = 0
    # number of deads
    step = 0

    
    rewardO = SimpleRewards(TOT_FRAME, TOT_SCORE)
    logdir = "logs/eating" + datetime.now().strftime("%Y:%m:%d--%H:%M:%S") + "-" + str(agent.MINIBATCH_SIZE)
    SAVE_NAME = "agent/eating-" + datetime.now().strftime("%Y:%m:%d--%H:%M:%S") + "-" \
    + str(agent.MINIBATCH_SIZE) 

    logger = TensorBoardLogger(logdir)
    

    while observation_num < TOT_FRAME:
        
        
        first = a.reset()
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
                if a.getScore() >= TOT_SCORE:
                    temp_done = True
                elif  observation_num % TOT_FRAMES_IN_LEVEL == (TOT_FRAMES_IN_LEVEL -1):
                    temp_done = True
                if im is not None:
                    im = im

                else:
                    # We will not use it anyway, so we create random image
                    #for batch calculation of our network
                    im = np.zeros(agent.model.input_shape[1:3])
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
                print("Earned a total of reward equal to ", rewardO.calculateTotalReward())
                logger.log_scalar("rewards", rewardO.calculateTotalReward(), step)
                
                
                loss_buf = []
                step+=1

            if observation_num % SAVE_FRAMES == 0:
                agent.save_network(SAVE_NAME)
                
        

            observation_num+=1
            logger.log_scalar("epsilon", agent.epsilon, observation_num)
            logger.log_scalar("AVG-loss", loss, observation_num)


    a.close()
