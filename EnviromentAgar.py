import subprocess
import sys
import time
from selenium import webdriver
import time
import grabimage as gi
import numpy as np
import os


TOP_BAR = 74
SETTINGS_NAME = {"set": ["showSkins", "darkTheme", "showGrid" ,"showBorder"],
                "unset": ["showNames", "showColor", "showMass",
                        "showChat", "showMinimap", "showPosition", "moreZoom",
                        "fillSkin", "backgroundSectors", "jellyPhysics", "playSounds"]}


class EnviromentAgar(object):

    def __init__(self, WINDOW_WIDTH, WINDOW_HIGHT, botsNumber = 0):
        
        self.discretized = False
        self.SCREENSHOT_MONITOR = {'top': 250, 'left': 0, 'width': WINDOW_WIDTH*2, 'height': WINDOW_HIGHT*2}
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HIGHT = WINDOW_HIGHT
        
        self.origWD = os.getcwd()
        
        os.chdir(os.path.join(os.path.abspath(sys.path[0]), "./OgarII/cli"))
        self.ogar = subprocess.Popen(["node", "index.js"],stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, encoding='utf8')
        os.chdir(self.origWD)

        os.chdir(os.path.join(os.path.abspath(sys.path[0]), "./Cigar2"))
        self.cigar = subprocess.Popen(["node", "webserver.js"], stdin=None, stdout=None)
        os.chdir(self.origWD)
        
        self.browser = webdriver.Firefox()
        self.browser.set_window_size(WINDOW_WIDTH, WINDOW_HIGHT + TOP_BAR)
        self.browser.set_window_position(0, 0)
        self.browser.get("http://localhost:3000")

        self.grabber = gi.ScreenShot(self.SCREENSHOT_MONITOR)
        self.images_generator = self.grabber.edited_images(84,84)

        self.canvas = self.browser.find_element_by_id("canvas")
        self.mouseHIGHT = int(self.canvas.get_attribute("height"))
        self.mouseWIDTH = int(self.canvas.get_attribute("width"))

        self.movementType = self.browser.find_element_by_id("dqnMovementType")

        self.mouseX = self.browser.find_element_by_id("dqnMouseX")
        self.mouseY = self.browser.find_element_by_id("dqnMouseY")
        self.score = self.browser.find_element_by_id("dqnScore")

        self.dead_box = self.browser.find_element_by_id("overlays")
        self.play_btn = self.browser.find_element_by_id("play-btn")
        



        self._initialSetup()
        
        self.setMoveType(False)

        self._setAction(1)
        self._addBot(botsNumber)

        
        self.setDiscretize()

        



    def isDead(self):
        return self.dead_box.value_of_css_property("display") == 'block'

    def getScore(self):
        return int(self.score.get_attribute("value"))

    def setDiscretize(self):
        self.discretized = not self.discretized
        self._sendCommand("discretize")


    def actionToMouse(self, action):
        switcher = {
                    0:(0,0),
                    1:(self.WINDOW_WIDTH//2,0),
                    2:(self.WINDOW_WIDTH,0),
                    3:(0,self.WINDOW_HIGHT//2),
                    4:(self.WINDOW_WIDTH//2,self.WINDOW_HIGHT//2),
                    5:(self.WINDOW_WIDTH,self.WINDOW_HIGHT//2),
                    6:(0,self.WINDOW_HIGHT),
                    7:(self.WINDOW_WIDTH//2,self.WINDOW_HIGHT),
                    8:(self.WINDOW_WIDTH,self.WINDOW_HIGHT)
                    }
        return switcher[action]

    def _setAction(self, action):
        x,y = self.actionToMouse(action)
        self.browser.execute_script("arguments[0].value = '{}';".format(x), self.mouseX)
        self.browser.execute_script("arguments[0].value = '{}';".format(y), self.mouseY)

    def setMoveType(self,mouse):
        if mouse:
            self.browser.execute_script("arguments[0].value = '0';", self.movementType) 
        else:
            self.browser.execute_script("arguments[0].value = '1';", self.movementType) 

    def _initialSetup(self):
        nick = 0
        while not nick:
            try:
                nick = self.browser.find_element_by_id("nick")
                nick.send_keys("DQN")
                skin = self.browser.find_element_by_id("skin")
                skin.send_keys("doge")
                nick.click()
                skin.click()

                for s in SETTINGS_NAME["set"]:
                    elem = self.browser.find_element_by_id(s)
                    print(s," ", elem.is_selected())
                    if not elem.is_selected():
                        elem.click()
                print("###############")
                for s in SETTINGS_NAME["unset"]:
                    elem = self.browser.find_element_by_id(s)
                    print(s," ", elem.is_selected())
                    if elem.is_selected():
                        elem.click()
            except:
                continue


    def setMoveType(self, mouse):
        e = self.browser.find_element_by_id("dqnMovementType")
        if mouse:
            self.browser.execute_script("arguments[0].value = '0';", e) 
        else:
            self.browser.execute_script("arguments[0].value = '1';", e) 


    def reset(self):
        self._sendCommand("killall 1")
        if self.isDead():
            self.play_btn.click()
        return next(self.images_generator)

    def step(self, action):
        self._setAction(action)
        self._sendCommand("next_step")
        score = self.getScore()
        image = next(self.images_generator)
        terminal = self.isDead()
        if terminal:
            return None, score, terminal
        return image, score, terminal

    def _addBot(self, count):
        self._sendCommand("addbot 1 {}".format(count))

    
    def _sendCommand(self, command):
        self.ogar.stdin.write(command + '\n')
        self.ogar.stdin.flush()
        time.sleep(0.005) #Time to reponse to command


    def close(self):
        self._sendCommand("exit")
        self.ogar.terminate()

        self.cigar.terminate()

        self.browser.close()

if __name__ == "__main__":
    a = EnviromentAgar(580,580)