from urllib import urlencode
from urllib2 import HTTPCookieProcessor, build_opener, install_opener
from urllib2 import getproxies, ProxyHandler
from HTMLParser import HTMLParser
import cookielib
import re
import time
import string
import random
import os
from modules.captchas import extractor


class MyParser(HTMLParser):
    def handle_data(self, data):
        if self.lasttag == 'li' and data.strip():
            print data


class Acesse(object):

    def __init__(self, username, password):

        # user variables
        self.username = username
        self.passwd = password

        # variable to save current web page
        self.page = None
        self.opener = None

        # create parser object
        self.parser = MyParser()

        # URLs used
        self.URL_LOGIN = "http://vservices.acesse.com/memberLogin.php?service=12&lang=1"
        self.URL_TURING = "http://vservices.acesse.com/turing.php"
        self.URL_SEARCH = "http://acesse.com/search.php?n={}&t=Web&q={}"

        # prepare search
        self.letters = string.ascii_lowercase + "+"  # letters used to make "words". + means space
        self.hashPattern = re.compile('name="n" value="(.+)" />')
        self.numberPattern = re.compile('<strong>(\d+)</strong>')

        # helper variables
        self.failed = 0
        self.searchNumber = 0
        self.origWordLength = 5
        self.wordLength = self.origWordLength
        self.origDelay = 5
        self.delay = self.origDelay
        self.loggedIn = False

        self.MAX_SENTENCE = 18  # max length of search sentence

        self.isUsingProxy = False

        self.setup()  # setup openers and probable proxies

    def setup(self):
        # install a cookie jar opener
        self.opener = build_opener(HTTPCookieProcessor(cookielib.MozillaCookieJar()))

        # if using proxy add it to opener
        hasProxy = getproxies()
        if hasProxy:
            print("Proxy found...Connecting...\n")
            proxy = ProxyHandler({'http': hasProxy['http']})
            # add proxy to opener
            self.opener.add_handler(proxy)
            self.isUsingProxy = True

        # add user agent to fool the servers
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) '
                                                 'AppleWebKit/535.1 (KHTML, like Gecko) '
                                                 'Chrome/13.0.782.13 Safari/535.1')]

        install_opener(self.opener)

    def login(self):

        # get session and download current turing image
        try:
            get_session = self.opener.open(self.URL_LOGIN, timeout=30)
            newImage = open("captcha.gif", "wb")
            newImage.write(self.opener.open(self.URL_TURING, timeout=30).read())
            newImage.close()
        except Exception:
            print "Failed to download captcha."
            return

        # get numbers from turing image
        try:
            if os.path.isfile("captcha.gif"):
                result = extractor("captcha.gif")
                os.remove("captcha.gif")  # unable to delete from extractor so delete here
            else:
                print "Unable to find captcha.gif file"
                return
        except Exception:
            print "Failed to get info from extractor method!"
            return

        # do some captcha result validation - 6 refers to length of captcha
        if result == -1 or len(str(result)) != 6 or not result.isdigit():
            print "Unable to read turing number"
            return

        # prepare payload
        data = {'username': self.username, 'passwd': self.passwd, 'turing': result, 'Login': 'Submit'}
        params = urlencode(data).encode()

        # open login page and login using payload
        try:
            handle = self.opener.open(self.URL_LOGIN, params, timeout=30)
            self.page = handle.read().decode("utf-8")
            self.parser.feed(self.page)
        except Exception:
            print "Failed to login with payload!"
            return

        # read initial value of the Search Number
        getNumber = re.search(self.numberPattern, self.page)
        if getNumber:
            self.searchNumber = int(getNumber.group(1))
            print "Account:", self.username
            print "Starting search Number:", self.searchNumber
            self.loggedIn = True
        else:
            print "Unable to get number!"
            return

    def run(self):
        # start search loop. Stop at MAX_SEARCH_NUMBER or if failed attempts == 3
        while self.searchNumber < MAX_SEARCH_NUMBER and self.failed < 3:
            getHash = re.search(self.hashPattern, self.page)
            if getHash:
                word = self.__makeword(self.wordLength)
                newURL = self.URL_SEARCH.format(getHash.group(1), word)

                # open the newUrl and process
                try:
                    handle = self.opener.open(newURL, timeout=30)
                    self.page = handle.read().decode('utf-8')
                except Exception:
                    print "Failed to process... Trying again\n"
                    self.failed += 1
                    continue

                # increase wordLength - make sure it's between origWordLength and MAX_SENTENCE
                self.wordLength = ((self.wordLength + random.randint(1, 2)) % self.MAX_SENTENCE)  # search word length
                if self.wordLength < self.origWordLength:
                    self.wordLength = self.origWordLength

                # read the search number
                getNumber = re.search(self.numberPattern, self.page)
                if getNumber:
                    num = int(getNumber.group(1))
                    if num == self.searchNumber:  # if search number is same, wait longer time
                        self.delay = int(self.origDelay * 2) if self.delay == self.origDelay else int(
                            self.origDelay * 3)  # 10 if prev delay == 5 else 15(.0)
                    else:
                        self.delay = self.origDelay  # reset delay
                        self.searchNumber = num  # update the search number value

                    print "Search Number:", num
                    self.failed = 0
                else:
                    print "Unable to get number!"
                    self.failed += 1

            else:
                print "Failed to get hashNumber!"
                self.failed += 1
            if self.searchNumber != MAX_SEARCH_NUMBER:  # delay if target number hasn't been reached
                for i in range(self.delay):
                    print ".",
                    time.sleep(2)
            print
        if self.failed == 3:
            self.loggedIn = False
            self.failed = 0

    def __makeword(self, length):
        word = ''
        last_char = None
        while len(word.strip(" +")) < length:
            char = random.choice(self.letters)
            if char == '+' and last_char == '+':
                char = self.letters[num - 1]
            last_char = char
            word += char
            if len(word) == length:
                word = word.strip(" +")  # don't need extra whitespace

        # check if any spaces has been inserted to longer words
        while word.count("+") < len(word) // 8:
            r = random.randint(3, len(word) - 3)
            left = word[r - 1] == '+'
            right = word[r + 1] == '+'
            middle = word[r] == '+'
            if not left and not right and not middle:
                word = word[:r] + "+" + word[r:]
        return word

    def logout(self):
        # logout
        try:
            handle = self.opener.open("http://acesse.com/logout.php?lang=1", timeout=30)
        except Exception:
            print "Failed to log out"
        else:
            print "Successfully logged out!"
        finally:
            self.opener.close()
            self.parser.close()
            self.loggedIn = False


def main():
    # the number of web searches to be made
    MAX_SEARCH_NUMBER = 50

    # user account information
    # ADD ALL ACCOUNTS AND PASSWORDS HERE
    #           accounts   passwords
    accounts = [("123456", "098765"),
                ("234567", "987654")]

    # main loop for all accounts
    while accounts:
        for account in accounts[:]:  # looping over a copy
            user = Acesse(*account)
            while user.searchNumber < MAX_SEARCH_NUMBER:
                if not user.loggedIn:
                    user.login()
                if user.loggedIn:
                    user.run()
                    user.logout()
                    if user.searchNumber >= MAX_SEARCH_NUMBER:
                        print "Account:", user.username, "done.\n"
                        accounts.remove(account)
                        del user
                        break  # to avoid getting 'user' not found error
                elif user.isUsingProxy and not getproxies():
                    user.setup()
                else:
                    print "..."
                    time.sleep(2 + 1)


if __name__ == '__main__':
    main()
    print "Program finished successfully."
    raw_input("Press enter to close...")
