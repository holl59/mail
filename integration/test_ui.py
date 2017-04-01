import os
import shutil
from os.path import dirname, join, exists

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
log_dir = join(LOG_DIR, 'app_log')


def test_web_with_selenium(user_domain, device_domain):

    os.environ['PATH'] = os.environ['PATH'] + ":" + join(DIR, 'geckodriver')

    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True
    caps["binary"] = "/usr/bin/firefox"

    profile = webdriver.FirefoxProfile()
    profile.set_preference("webdriver.log.file", "{0}/firefox.log".format(log_dir))
    driver = webdriver.Firefox(profile, capabilities=caps)

    wait_driver = WebDriverWait(driver, 20)

    screenshot_dir = join(DIR, 'screenshot')
    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)

    driver.get("http://{0}".format(user_domain))
    
    time.sleep(2)
    driver.get_screenshot_as_file(join(screenshot_dir, 'login.png'))

    print(driver.page_source.encode("utf-8"))

    user = driver.find_element_by_id("rcmloginuser")
    user.send_keys(DEVICE_USER)
    password = driver.find_element_by_id("rcmloginpwd")
    password.send_keys(DEVICE_PASSWORD)
    driver.get_screenshot_as_file(join(screenshot_dir, 'login.png'))
    password.send_keys(Keys.RETURN)

    #time.sleep(10)

    username = '{0}@{1}'.format(DEVICE_USER, device_domain)
    #print('found: {0}'.format(username in page))
    wait_driver.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.username'), username))

    driver.get_screenshot_as_file(join(screenshot_dir, 'main.png'))

    page = driver.page_source.encode("utf-8")
    print(page)






    