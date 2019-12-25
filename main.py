from selenium import webdriver
import time
import grabimage as gi
import numpy as np
import EnviromentAgar as EA
import random



TOP_BAR = 74
BROWSER_WIDTH = 580
BROWSER_HIGHT = 580 + TOP_BAR
SCREENSHOT_MONITOR = {'top': 250, 'left': 0, 'width': BROWSER_WIDTH*2, 'height': (BROWSER_HIGHT - TOP_BAR)*2}

SETTINGS_NAME = {"set": ["showSkins", "darkTheme", "showGrid" ,"showBorder"],
                "unset": ["showNames", "showColor", "showMass",
                        "showChat", "showMinimap", "showPosition", "moreZoom",
                        "fillSkin", "backgroundSectors", "jellyPhysics", "playSounds"]}


DECAY_RATE = 0.99
BUFFER_SIZE = 40000
MINIBATCH_SIZE = 64
TOT_FRAME = 3000000
EPSILON_DECAY = 1000000
MIN_OBSERVATION = 5000
FINAL_EPSILON = 0.05
INITIAL_EPSILON = 0.1
NUM_ACTIONS = 6
TAU = 1000
# Number of frames to throw into network
NUM_FRAMES = 3


if __name__ == "__main__":
    a = EA.EnviromentAgar(580,580, botsNumber=50)
    first = a.reset()
    #gi.ScreenShot.show(first)
    last = None
    while True:
        im, score= a.step(random.randint(0,8))
        if im is None:
            time.sleep(2)
            a.reset()
            time.sleep(2)
        print(score)
        time.sleep(0.01)
    print(a.isDead())
    input()
    a.close()
