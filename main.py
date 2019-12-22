from selenium import webdriver
import time
import grabimage as gi

TOP_BAR = 80
WIDTH = 580
HIDTH = 320 + TOP_BAR
MONITOR = {'top': 250, 'left': 0, 'width': WIDTH*2, 'height': int(HIDTH*1.6)}

SETTINGS_NAME = {"set": ["showSkins", "darkTheme", "showGrid" ,"showBorder"],
                "unset": ["showNames", "showColor", "showMass",
                        "showChat", "showMinimap", "showPosition", "moreZoom",
                        "fillSkin", "backgroundSectors", "jellyPhysics", "playSounds"]}


def main():
    browser = webdriver.Firefox()
    browser.set_window_size(WIDTH, HIDTH)
    browser.set_window_position(0, 0)
    browser.get("http://localhost:3000")

    time.sleep(1)
    
    nick = 0

    while not nick:
        try:
            nick = browser.find_element_by_id("nick")
            nick.send_keys("DQN")
            skin = browser.find_element_by_id("skin")
            skin.send_keys("doge")


            #
            nick.click()
            skin.click()

            for s in SETTINGS_NAME["set"]:
                elem = browser.find_element_by_id(s)
                print(s," ", elem.is_selected())
                if not elem.is_selected():
                    elem.click()
            print("###############")
            for s in SETTINGS_NAME["unset"]:
                elem = browser.find_element_by_id(s)
                print(s," ", elem.is_selected())
                if elem.is_selected():
                    elem.click()

            time.sleep(1)

            element = browser.find_element_by_id("play-btn")
            element.click()

        except:
            continue

    grabber = gi.ScreenShot(MONITOR)
    score = browser.find_element_by_id("dqnScore")

    #for image in grabber.edited_images(MONITOR["width"]//2,MONITOR["height"]//2):
    for image in grabber.edited_images(110,84):
        print("Score: ", score.get_attribute("value"), end='\r')
        gi.ScreenShot.show(image)

    
    time.sleep(2)
    browser.close()

if __name__ == "__main__":
    main()
