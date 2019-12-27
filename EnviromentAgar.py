import subprocess
import sys
import time
from selenium import webdriver
import time
import grabimage as gi
import numpy as np
import os
import socket


TOP_BAR = 74
SETTINGS_NAME = {"set": ["showSkins", "darkTheme", "showGrid" ,"showBorder"],
                "unset": ["showNames", "showColor", "showMass",
                        "showChat", "showMinimap", "showPosition", "moreZoom",
                        "fillSkin", "backgroundSectors", "jellyPhysics", "playSounds"]}


class EnviromentAgar(object):

    def __init__(self, WINDOW_WIDTH, WINDOW_HIGHT, botsNumber = 0, PORT=2998):
        f = open("Ogar_o.txt","w")
        self.discretized = False
        self.SCREENSHOT_MONITOR = {'top': 250, 'left': 0, 'width': WINDOW_WIDTH*2, 'height': WINDOW_HIGHT*2}
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HIGHT = WINDOW_HIGHT
        
        self.origWD = os.getcwd()
        
        os.chdir(os.path.join(os.path.abspath(sys.path[0]), "./OgarII/cli"))
        self.run_ogar = subprocess.Popen(["node", "index.js"],stdin=subprocess.DEVNULL,
    stdout=f, encoding='utf8')
        os.chdir(self.origWD)

        os.chdir(os.path.join(os.path.abspath(sys.path[0]), "./Cigar2"))
        self.run_cigar = subprocess.Popen(["node", "webserver.js"], stdin=subprocess.DEVNULL,
         stdout=subprocess.DEVNULL)
        os.chdir(self.origWD)

        self._connectToOgar(PORT)
        
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
        command = command.encode()
        self.socket.sendall(command + b"\r\n")
        recv = []
        while True:
            chunck = self.socket.recv(1)
            recv.append(chunck)
            if chunck == b'\n':
                break
            

        recv = b"".join(recv)
        if recv != b"OK\r\n":
            print("!!!, Error in response")
            raise ConnectionError()
        time.sleep(0.005)

    def _connectToOgar(self, port, count = 3):
        c = 0
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect(('127.0.0.1',2998))
                return
            except:
                self.socket.close()
                if c >= count:
                    break
                else:
                    c+=1
                    time.sleep(0.5)
                    continue
        raise ConnectionError("Can not connect to node")
                



    def close(self):
        self._sendCommand("exit")
        self.run_ogar.terminate()

        self.run_cigar.terminate()

        self.browser.close()

if __name__ == "__main__":
    a = EnviromentAgar(580,580)