import mss
import numpy as np
import mss.tools
import time
import cv2


class ScreenShot(object):

    """Docstring for ScreenShot. """

    def __init__(self, monitor = {'top': 0, 'left': 0, 'width': 800, 'height': 600}, fps = 30):
        """TODO: to be defined1.

        :monitor: TODO
        :fps: TODO

        """
        self._monitor = monitor
        self._spf = (1/fps)
        self._sct = mss.mss()

    
    def images(self):
        while True:
            self.start = time.time()
            shoot = np.array(self._sct.grab(self._monitor))
            
            self.temp = time.time() - self.start
            

            if self.temp < self._spf:
                time.sleep(self._spf - self.temp)
            

            yield shoot
    
    def edited_images(self, height, width):
        for shot in self.images():
            image = cv2.cvtColor(shot, cv2.COLOR_RGB2GRAY)

            yield cv2.resize(image,(height,width)).astype(np.float32) 


    def show(image):
        cv2.imshow('window', image)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()


if __name__ == "__main__":
    s = ScreenShot()
    for i in s.edited_images(1600,1600):
        ScreenShot.show(i)
        continue



