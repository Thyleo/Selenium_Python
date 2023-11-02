'''
Author : Hassan Ali Hassan
Contact : hassanalihassan1540@gmail.com
'''

import logging
import os
import shutil
import time
import random
import threading
from datetime import datetime
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver import ActionChains, DesiredCapabilities
import pathlib
import platform
import psutil
import sqlite3
import mymodulesteam
from mymodulesteam import LoadFile

open(mymodulesteam.LoadFile('log.log'), 'w').close()
logger = logging.getLogger('__Browser_auto_follow_instagram__')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s')
file_handler = logging.FileHandler(mymodulesteam.LoadFile('log.log'))
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

insta_username = "perpi007"
insta_password = "54848455Eli"
# ================================================================================
# ================= Send action to action table ==================================

def Inser_Value_To_action(date_created, id_contact, user_id, plateform = str("Instagram")):
    try:
        conn = sqlite3.connect(LoadFile('db.db'))
        cursor = conn.cursor()
        insert_query = """INSERT INTO actions(platform, type_action, date, id_contact, date_created,
                        id_task_user) VALUES(?, ?, ?, ?, ?, ?) """
        action_tuple = (
            plateform, "follow", date_created, id_contact,
            str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), user_id)
        cursor.execute(insert_query, action_tuple)
        conn.commit()
        conn.close()
    except Exception as ex:
        logger.error(f'sqlite execption (Inser_Value_To_action): {ex}')
        return False
    return True


def Sleeping_Bot(borne_inf=float, borne_sup=float):
    """
        Random time.sleep for being a stealth bot.
    """
    ts = random.uniform(borne_inf, borne_sup)
    ts = round(ts, 2)
    time.sleep(ts)
# ================================= send contacts to contacts table =========================
def Inser_Value_To_contact(user_id, name, plateform=str("Instagram")):
    date_created = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        conn = sqlite3.connect(LoadFile('db.db'))
        cursor = conn.cursor()
        insert_query = """INSERT INTO contacts(platform, username, id_task_user, date_created) 
                            VALUES (?, ?, ?, ?) """
        contact_tuple = (plateform, name, user_id, date_created)
        cursor.execute(insert_query, contact_tuple)
        conn.commit()

        contact_id = cursor.execute("SELECT id FROM contacts WHERE username = ? AND date_created = ?",
                                    [name, date_created]).fetchone()[0]
        conn.close()
        return Inser_Value_To_action(date_created, contact_id, user_id)
    except Exception as ex:
        logger.error(f'Exception thrown (Inser_Value_To_contact): {ex} {ex.__cause__}')
        return False


def get_url_list(url):
    if url is None:
        logger.info(f'url spreadsheet not found')
        return False
    return mymodulesteam.GoogleSheetGetValues(mymodulesteam.extract_ss_id_regex(url))


def scroll_down(driver):
    """A method for scrolling the page."""
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        logger.info('no more followers')
        return True

    last_height = new_height
    return False


def click_on_element(driver, element):
    driver.execute_script("arguments[0].click();", element)


def follow_button(driver, action_done, follow_number, p_taskuser_id):
    # Init list
    followButton = []
    action = True
    isEnd = False
    while action and not isEnd:
        try:
            # RECUPERE LES BOUTTONS FOLLOW AVEC LEUR XPATH S’abonner
            buttons = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, (
                "div.YBx95>button.y3zKF"))))

            # RECUPERE LES NOMS de FOLLOW AVEC LEUR XPATH
            names = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, "span.Jv7Aj>a.FPmhX")))

            for button in buttons:
                if button not in followButton:
                    followButton.append(button)
                    click_on_element(driver, button)
                    time.sleep(random.uniform(1, 1.2))
                    #confirm = driver.find_element_by_xpath(
                        #"//button[@type='button']")
                    #followButton.append(confirm)
                    #click_on_element(driver, confirm)
                    print("follow is confirmed")
                    time.sleep(random.uniform(1, 2))

                    name = names[buttons.index(button)].text

                    name = name[1:]
                    Inser_Value_To_contact(p_taskuser_id, name)
                    action_done += 1

                if action_done == follow_number:
                    logger.info(f'the work for {follow_number} action is already done')
                    action = False
                    break

            isEnd = scroll_down(driver)

        except TimeoutException:
            logger.info('not found any followers in the page scroll down')
            isEnd = scroll_down(driver)

        except Exception as ex:
            logger.error(f'Didn\'t not found any followers : {ex}')
            return False


def Browser_Instagram_Auto_Follow(p_browser, follow_number):
    logger.info("=== [1] Open Browser =======================================")
    action_done = 0
    task = mymodulesteam.GetDetailsTaskUser(p_taskuser_id)

    # OUVERTURE DU NAVIGATEUR
    if p_browser == "Chrome":
        driver = mymodulesteam.ChromeDriverWithProfile()
    elif p_browser == "Firefox":
        driver = mymodulesteam.FireFoxDriverWithProfile()
    else:
        logger.error(f"PhoneBot didn't find the browser called '{p_browser}'.")

    driver.maximize_window()
    try:

        # CHARGEMENT DE LA PAGE
        driver.get('https://www.instagram.com/')
        driver.implicitly_wait(10)
        # cliquer sur le pop up des cookies
        #cookiesAcceptButton = WebDriverWait(driver, 10).until(
        #    EC.presence_of_element_located((By.CSS_SELECTOR, ("button.aOOlW.bIiDR"))))
        #driver.execute_script("arguments[0].click();", cookiesAcceptButton)
        #Sleeping_Bot(2.0, 12.0)
        #driver.implicitly_wait(10)

        # Connection
        usernameTextInput = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ("input[type='text']"))))
        for letter in insta_username:
            usernameTextInput.send_keys(letter)
            Sleeping_Bot(0.1, 1.5)

        passwordTextInput = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ("input[type='password']"))))
        for letter in insta_password:
            passwordTextInput.send_keys(letter)
            Sleeping_Bot(0.1, 1.5)

        connectionButton = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ("button[type='submit']"))))
        Sleeping_Bot(2.0, 12.0)
        driver.execute_script("arguments[0].click();", connectionButton)
        driver.implicitly_wait(10)
        urlprofile = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, ("//body/div[@id='react-root']/section[1]/nav[1]/div[2]/div[1]/div[1]/div[3]/div[1]/div[5]/span[1]/img[1]"))))
        Sleeping_Bot(2.0, 12.0)
        driver.execute_script("arguments[0].click();", urlprofile)
        driver.implicitly_wait(5)
        profile= WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, ("//div[contains(text(),'Profil')]"))))
        Sleeping_Bot(2.0, 12.0)
        driver.execute_script("arguments[0].click();", profile)
        # # TROUVER LE BOUTTON DES Abonnés
        followersButton = driver.find_element_by_xpath(
            "/html[1]/body[1]/div[1]/section[1]/main[1]/div[1]/header[1]/section[1]/ul[1]/li[2]/a[1]")
        time.sleep(random.uniform(1, 3))
        # VA SUR LA PAGE DES FOLLOWERS
        click_on_element(driver, followersButton)
        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight;', followersButton)
        driver.execute_script(
            'arguments[0].scrollTop = 0;', followersButton)
        listOfFollow= WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, ("/html/body/div[5]/div/div/div[2]/div[3]/a"))))
        Sleeping_Bot(2.0, 12.0)
        driver.execute_script("arguments[0].click();", listOfFollow)
        driver.implicitly_wait(5)


        follow_button(driver, action_done, follow_number, p_taskuser_id)


    except Exception as ex:
        logger.error(f'url not defined {ex}')
        return False

    finally:
        driver.quit()


p_browser = "Firefox"
p_taskuser_id = "254"
follow_number = 5
Browser_Instagram_Auto_Follow(p_browser, follow_number)