from selenium import webdriver
import time
import grabimage as gi
import numpy as np
import EnviromentAgar as EA
import random
from DeepQModel import DeepQModel



TOP_BAR = 74
BROWSER_WIDTH = 580
BROWSER_HIGHT = 580 + TOP_BAR
SCREENSHOT_MONITOR = {'top': 250, 'left': 0, 'width': BROWSER_WIDTH*2, 'height': (BROWSER_HIGHT - TOP_BAR)*2}

SETTINGS_NAME = {"set": ["showSkins", "darkTheme", "showGrid" ,"showBorder"],
                "unset": ["showNames", "showColor", "showMass",
                        "showChat", "showMinimap", "showPosition", "moreZoom",
                        "fillSkin", "backgroundSectors", "jellyPhysics", "playSounds"]}

TOT_FRAME = 3000000
MIN_OBSERVATION = 5000
NUM_ACTIONS = 9
NUM_FRAMES = 3



if __name__ == "__main__":
    a = EA.EnviromentAgar(580,580, botsNumber=50)
    agent = DeepQModel(NUM_ACTIONS,NUM_FRAMES)

    observation_num = 0
    

    while observation_num < TOT_FRAME:
        
        first = a.reset()/255
        input()
        state = np.array([first]*NUM_FRAMES)
        state = np.moveaxis(state,0,NUM_FRAMES - 1)
        alive_frame = 0
        total_reward = 0

        done = False
        
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
                    im = np.random.rand(*agent.model.input_shape[1:3])
                buffer.append(im)
                done = done | temp_done
                temp_rewards.append(temp_reward)

            
            if done:
                reward = -1
            
            else:
                reward = max(temp_rewards)

            next_state = np.array(buffer)
            next_state = np.moveaxis(next_state, 0, NUM_FRAMES - 1)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward = reward

            if len(agent.memory) > MIN_OBSERVATION:
                agent.replay()

            if done:
                print("Lived with maximum time ", alive_frame)
                print("Earned a total of reward equal to ", total_reward)
                
        

            observation_num+=1
            alive_frame+=1


    a.close()
