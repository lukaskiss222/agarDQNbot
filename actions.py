import numpy as np






class Actions(object):


    def __init__(self, canvas_width, canvas_height):
        self.width = canvas_width
        self.height = canvas_height
    
        self.actions = np.identity(9)




    def actionToVector(self, action):
        return self.actions[action]

    def actionToMouse(self, action):
        switcher = {
                0:(0,0),
                1:(canvas_width//2,0),
                2:(canvas_width,0),
                3:(0,canvas_height//2),
                4:(canvas_width//2,canvas_height//2),
                5:(canvas_width,canvas_height//2),
                6:(0,canvas_height),
                7:(canvas_width//2,canvas_height),
                8:(canvas_width,canvas_height)
                }
        return switcher[action]





