from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep


class Robot(object):
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd

        self.surfed_sites = 0

        # constants
        self.URL_LOGIN = r"http://vservices.acesse.com/memberLogin.php?service=11&lang=1"
        self.URL_LOGOUT = r"http://acesse.com/?lang=1"
        self.CAPTCHA_LIST = [5, 10, 15, 20, 25]
        self.STAR_2 = r"/html/body/table/tbody/tr[1]/td[1]/div/div[4]/form/div[1]/span/a[2]"
        self.STAR_3 = r"/html/body/table/tbody/tr[1]/td[1]/div/div[4]/form/div[1]/span/a[3]"

        self.isLoggedIn = False

        # setup window and adjust size and position
        size = self.getDisplaySize()  # gets the current monitor size
        sizeX = int(size[0] / 3. - (4 * 2))  # gets size of each window X
        sizeY = int(size[1] / 2. - (4 * 3) - 13)  # gets size of each window Y
        
        self.browser = webdriver.Firefox()
        self.browser.set_window_size(sizeX, sizeY)
        self.browser.set_window_position(4, 4)

    def getDisplaySize(self):
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height

    def login(self):

        # go to login page
        self.browser.get(self.URL_LOGIN)

        # enter username
        self.browser.find_element_by_name("username").send_keys(self.username)

        # loop until user successfully logs in
        while self.browser.current_url == self.URL_LOGIN:
            # enter password in form
            self.browser.find_element_by_name("passwd").send_keys(self.passwd)

            # move focus to the captcha field
            self.browser.find_element_by_name("turing").send_keys(Keys.NULL)

            # wait for user to type captcha - the crude way
            while len(self.browser.find_element_by_name("turing").get_attribute("value")) < 6:
                sleep(0.5)
                continue
            self.browser.find_element_by_name("Login").click()

        # get the current surfed sites number
        self.surfed_sites = int(self.browser.find_element_by_class_name("ajax_sites_surfed").text)

        self.isLoggedIn = True

    def run(self):
        # main loop
        while self.surfed_sites < MAX_SURFED_SITES:
            try:
                # waiting for timer
                WebDriverWait(self.browser, 50).until(
                    EC.element_to_be_clickable((By.ID, 'nextAd')))

                # update new value
                self.surfed_sites = int(self.browser.find_element_by_class_name("ajax_sites_surfed").text)

                # if timer has reached 0
                # first check that turing is not displayed - crude way
                if self.surfed_sites in self.CAPTCHA_LIST:
                    # click on 2 stars
                    WebDriverWait(self.browser, 50).until(
                        EC.element_to_be_clickable((By.ID, 'nextAd')))
                    self.browser.find_element_by_xpath(self.STAR_2).click()

                    # move focus to the captcha field
                    self.browser.find_element_by_id("turing").send_keys(Keys.NULL)

                    # wait until user has typed the 4 captcha numbers
                    while len(self.browser.find_element_by_id("turing").get_attribute("value")) < 4:
			sleep(0.5)
                        continue
                    self.browser.find_element_by_id("nextAd").click()

                else:
                    # give 3 stars
                    WebDriverWait(self.browser, 50).until(
                        EC.element_to_be_clickable((By.ID, 'nextAd')))
                    self.browser.find_element_by_xpath(self.STAR_3).click()
                    self.browser.find_element_by_id("nextAd").click()

                # update new value
                WebDriverWait(self.browser, 50).until(
                    EC.visibility_of((By.ID, 'timer')))
                self.surfed_sites = int(self.browser.find_element_by_class_name("ajax_sites_surfed").text)

                if self.surfed_sites >= MAX_SURFED_SITES:
                    return

            except Exception:
                continue

    def logout(self):
        while self.browser.current_url != self.URL_LOGOUT:
            self.browser.get(self.URL_LOGOUT)
        self.isLoggedIn = False

# main program
def main():

    # number of ad searches to be made
    MAX_SURFED_SITES = 26

    # add accounts here
    accounts = [("123456", '098765')]

    # looping over all accounts
    while accounts:
        for account in accounts[:]:
            bot = Robot(*account)
            bot.login()
            bot.run()
            if bot.surfed_sites >= MAX_SURFED_SITES:
                if bot.isLoggedIn:
                    bot.logout()
                if not bot.isLoggedIn:
                    bot.browser.quit()

if __name__ == '__main__':
    main()
