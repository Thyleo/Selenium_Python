# -*- coding: utf-8 -*-

"""
This module contain some modules from mymodules.py improved by other developpers
https://github.com/phonebotco/phonebot
"""
import logging
import os
import random
import re
import shutil
import sqlite3
import time

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
from google.oauth2 import service_account #  pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from googleapiclient.discovery import build
import google_auth_httplib2


def LoadFile(p_file):
    # 1rst we need to split the filename in name and extension
    p_file_split = str(p_file).split('.')
    p_name = p_file_split[0]
    if len(p_file_split) == 2:
        p_ext = p_file_split[1]
    elif len(p_file_split) == 1:
        p_ext = None
    elif len(p_file_split) > 2:
        p_name = ''
        for i in range(0, len(p_file_split) - 2):
            p_name += p_file_split[i]
        p_ext = p_file_split[len(p_file_split) - 1]

    # Let's create the HOME/PhoneBot directory

    # print(f"p_name :{p_name}")
    # print(f"p_ext :{p_ext}")
    if platform.system() == 'Darwin':
        from AppKit import NSBundle
        # FOR MAC WE NEED FULL PATH, SO LET's PREPARE IT
        HOME_DIR = os.environ['HOME']
        # If folder /PhoneBot in user's home doesn't exist
        if not os.path.isdir(HOME_DIR + '/PhoneBot'):
            os.mkdir(HOME_DIR + '/PhoneBot')
        HOME_PHONEBOT_DIR = HOME_DIR + '/PhoneBot'
        UI_DIR = HOME_PHONEBOT_DIR + '/ui'
        test_if_PhoneBot_app = NSBundle.mainBundle().pathForResource_ofType_(p_name, p_ext)
        # 2 For Mac, we need to check if there we are in Applications/PhoneBot.app or not

        if p_file == 'ui.json':
            # We need to test if ui.json exist in user's home folder, if not we copy paste it
            file_ui_json = pathlib.Path(HOME_PHONEBOT_DIR + '/ui.json')

            print(f"{file_ui_json}  - {type(file_ui_json)}")
            curpath = os.path.abspath(os.curdir)
            print(f"curpath : {curpath}")
            print(f"HOME_PHONEBOT_DIR + '/ui.json' : {HOME_PHONEBOT_DIR + '/ui.json'}")
            if not file_ui_json.exists():

                shutil.copyfile(curpath + '/ui.json', HOME_DIR + '/ui.json')
            elif file_ui_json.exists():
                # If ui.json in program folder is more recent that ui.json of home folder,
                # we copy paste the most recent
                mtime_uijson_home = os.path.getmtime(HOME_PHONEBOT_DIR + '/ui.json')
                mtime_uijson_program = os.path.getmtime(curpath + '/ui.json')

                if mtime_uijson_home < mtime_uijson_program:
                    shutil.copy(curpath + '/ui.json', HOME_PHONEBOT_DIR + '/ui.json')
                    # shutil.move(os.path.join(curpath , 'ui.json'), os.path.join(HOME_DIR, 'ui.json'))
                    logger.info(f"ui.json file was copied from application folder to home folder")
                else:
                    logger.info(
                        f"ui.json file from your home directory is more recent than the one in applications folder")

        if test_if_PhoneBot_app is None:
            # WE ARE NOT IN PHONEBOT APP
            # ALSO WE HAVE 2 KINDS OF FILES: THE ONES WE READ ONLY AND THE ONES WE WILL MODIFY
            # FOR THE ONES WE MODIFY OR CREATE, WE NEED TO CHANGE LOCATION TO HOME/PhoneBot
            if p_file == 'log.log' or p_file == 'db.db' or p_file == 'config.ini' or p_file == 'tmp.txt' or p_file == 'ui.txt' \
                    or p_file == 'appium.log' or p_file == 'appium.zip' or p_file == 'log.zip':
                # WE NEED TO CHECK IF THE FOLDER HOME/PhoneBot
                result = HOME_PHONEBOT_DIR + '/' + p_file
            # elif p_file == 'ui.json':
            #     # WE NEED TO CHECK IF THE FOLDER HOME/PhoneBot exist or not
            #     result = HOME_PHONEBOT_DIR + '/' + p_file
            else:
                result = p_file
        else:
            # WE ARE IN PHONEBOT APP
            # ALSO WE HAVE 2 KINDS OF FILES: THE ONES WE READ ONLY AND THE ONES WE WILL MODIFY
            # FOR THE ONES WE MODIFY OR CREATE, WE NEED TO CHANGE LOCATION TO HOME/PhoneBot
            if p_file == 'log.log' or p_file == 'db.db' or p_file == 'config.ini' or p_file == 'tmp.txt' or p_file == 'ui.txt' \
                    or p_file == 'appium.log' or p_file == 'appium.zip' or p_file == 'log.zip':

                # print(f"p_file is : {p_file}")
                # WE NEED TO CHECK IF THE FOLDER HOME/PhoneBot
                result = NSBundle.mainBundle().pathForResource_ofType_(HOME_PHONEBOT_DIR + '/' + p_name, p_ext)
                # print(f"result for log,db,config: {result}")

            # elif p_file == 'ui.json':
            #
            #     print(f"p_file is : {p_file}")
            #     #result = NSBundle.mainBundle().pathForResource_ofType_(p_name, p_ext)
            #     result = NSBundle.mainBundle().pathForResource_ofType_(HOME_PHONEBOT_DIR + '/' + p_name, p_ext)
            #     print(f"result for ui.json: {result}")
            else:
                # print(f"p_file is : {p_file}")
                result = NSBundle.mainBundle().pathForResource_ofType_(p_name, p_ext)
                # print(f"result for else : {result}")
    else:
        result = p_file

    # print(f"result : {result}")
    return result



open(LoadFile('log.log'), 'w').close()
logger = logging.getLogger('__mymodulesteam__')
logger.setLevel(logging.INFO)
formatter=logging.Formatter('%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s')
file_handler = logging.FileHandler(LoadFile('log.log'))
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# ================================================================================
# FUNCTION DE CREATION DE DRIVER CHROME OU FIREFOX


def all_subdirs_of(b='.'):
    """
    This function return all the subdorectories of a directory
    """

    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd): result.append(bd)
    return result


def KillProgram(p_program):
    logger.info(
        f"=================================== KillProgram {p_program} ===========================================")
    if platform.system() == 'Windows':
        PROCNAME = p_program + ".exe"
        # print(f"PROCNAME : {PROCNAME}")


    elif platform.system() == 'Darwin':
        PROCNAME = p_program

    for proc in psutil.process_iter():
        # print(f"proc.name() : {proc.name()}")

        if proc.name() == PROCNAME:
            # print(proc)
            # print(f"PhoneBot will kill this process : {proc}")
            try:
                proc.kill()
            except Exception as ex:
                logger.error(f"{ex} - PhoneBot couldn't kill the process")


def ChromeDriverWithProfile():
    """
    This function will return the chrome driver with the Chrome profile loaded
    """
    # We need to close all the instances of Chrome or it will bug
    KillProgram('chrome')

    chrome_profile_path= r"%LocalAppData%\Google\Chrome\User Data"
    chrome_profile_path = os.path.expandvars(chrome_profile_path)

    print(f"chrome_profile_path : {chrome_profile_path}")
    chrome_options = Options()

    chrome_options.add_argument(r"--user-data-dir=" + chrome_profile_path)
    chrome_options.add_argument("--disable-extensions")

    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-session-crashed-bubble")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # overcome limited resource problems
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Bypass OS security model
    chrome_options.add_argument("--no-sandbox")
    # We need to remove the bubble popup 'Restore pages' of Chrome:
    # https://dev.to/cuongld2/get-rid-of-chrome-restore-bubble-popup-when-automate-gui-test-using-selenium-3pmh
    preference_file = chrome_profile_path + "\\Default\\Preferences"
    string_to_be_change='"exit_type":"Crashed"'
    new_string='"exit_type": "none"'
    #read input file
    fin = open(preference_file, "rt")
    #read file contents to string
    data = fin.read()
    #replace all occurrences of the required string
    data = data.replace(string_to_be_change, new_string)
    #close the input file
    fin.close()
    #open the input file in write mode
    fin = open(preference_file, "wt")
    #overrite the input file with the resulting data
    fin.write(data)
    #close the file
    fin.close()

    driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    return driver


def FireFoxDriverWithProfile():
    print( "==================== FireFoxDriverWithProfile =======================")
    """
    This function will return the chrome driver with the FireFox profile loaded
    """
    # We need to close all the instances of Firefox or it will bug
    KillProgram('firefox')


    firefox_profile_folder_path = appdata =os.environ['APPDATA'] + "\Mozilla\Firefox\Profiles"
    latest_profile = max(all_subdirs_of(firefox_profile_folder_path), key=os.path.getmtime)
    print(f"profile : {latest_profile}")
    profile = FirefoxProfile(latest_profile)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.update_preferences()
    desired = DesiredCapabilities.FIREFOX

    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), firefox_profile=profile, desired_capabilities=desired)

    print(f"profile : {profile}")

    return driver


def GetDetailsTaskUser(p_taskuser_id):
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate (cursor.description):
            d[col[0]] = row[idx]
        return d
    # Connect to SQLITE
    sqlite_connection = sqlite3.connect (LoadFile ('db.db'))
    sqlite_connection.row_factory = dict_factory
    sqlite_cursor = sqlite_connection.cursor ()
    taskuser_details_dico=sqlite_cursor.execute("SELECT id,enable,id_task,id_campaign,url_keywords,minimum,url_list,  \
            url_usernames,message_txt_invitation_1B,message_txt_1A,message_txt_2A,message_txt_3A,message_txt_4A,  \
            message_voice_1A,message_voice_2A,message_voice_3A,message_voice_4A,message_txt_invitation_1A,message_txt_1B,  \
            message_txt_2B,message_txt_3B,message_txt_4B,message_voice_1B,message_voice_2B,message_voice_3B,  \
            message_voice_4B,date_counter_test_AB,time_delay_1A,time_delay_1A_type,time_delay_2A,time_delay_2A_type,  \
            time_delay_3A,time_delay_3A_type,time_delay_1B,time_delay_1B_type,time_delay_2B,time_delay_2B_type,  \
            time_delay_3B,time_delay_3B_type,message_1A_choice,message_2A_choice,message_3A_choice,message_4A_choice,  \
            message_1B_choice,message_2B_choice,message_3B_choice,message_4B_choice,AB_testing_enable,AB_testing_enable_invitation,  \
            date_AB_testing,date_AB_testing_invitation,serie_type,daily_limit  \
            FROM tasks_user where id=?",(p_taskuser_id,)).fetchone()
    return taskuser_details_dico



def random_abc(text_data):
    """
    Function to replace the random_abc synonyms by one word. It will pick up randomly one of the words
    :param text_data:
    :return:
    """
    random_txt_group = re.findall("\{random_abc:(.*?)\}", text_data)
    for random_txt in random_txt_group:
        random_txt_list = random_txt.split('|')
        text_data = text_data.replace('{random_abc:' + random_txt + '}', random.choice(random_txt_list))
    return text_data

# =========================================================================================
# ================================== Google Sheet functions ===============================
# =========================================================================================

def GoogleSheetGetValues(p_sheet_id):
    """
    This function go to Google sheet and get all the values. It will return a list of list like this:
    [['test 1', 'test 2', 'test 3', 'test 4', 'test 5', 'test 6', 'test 7'], ['test 2', 'test 3', 'test 4', 'test 5', 'test 6', 'test 7', 'test 8'], ['test 3', 'test 4', 'test 5', 'test 6', 'test 7', 'test 8', 'test 9'], ['test 4', 'test 5', 'test 6', 'test 7', 'test 8', 'test 9', 'test 10'], ['test 5', 'test 6', 'test 7', 'test 8', 'test 9', 'test 10', 'test 11'], ['test 6', 'test 7', 'test 8', 'test 9', 'test 10', 'test 11', 'test 12'], ['test 7', 'test 8', 'test 9', 'test 10', 'test 11', 'test 12', 'test 13'], ['test 8', 'test 9', 'test 10', 'test 11', 'test 12', 'test 13', 'test 14'], ['test 9', 'test 10', 'test 11', 'test 12', 'test 13', 'test 14', 'test 15'], ['test 10', 'test 11', 'test 12', 'test 13', 'test 14', 'test 15', 'test 16'], ['test 11', 'test 12', 'test 13', 'test 14', 'test 15', 'test 16', 'test 17'], ['test 12', 'test 13', 'test 14', 'test 15', 'test 16', 'test 17', 'test 18'], ['test 13', 'test 14', 'test 15', 'test 16', 'test 17', 'test 18', 'test 19'], ['test 14', 'test 15', 'test 16', 'test 17', 'test 18', 'test 19', 'test 20'], ['test 15', 'test 16', 'test 17', 'test 18', 'test 19', 'test 20', 'test 21'], ['test 16', 'test 17', 'test 18', 'test 19', 'test 20', 'test 21', 'test 22'], ['test 17', 'test 18', 'test 19', 'test 20', 'test 21', 'test 22', 'test 23'], ['test 18', 'test 19', 'test 20', 'test 21', 'test 22', 'test 23', 'test 24'], ['test 19', 'test 20', 'test 21', 'test 22', 'test 23', 'test 24', 'test 25'], ['test 20', 'test 21', 'test 22', 'test 23', 'test 24', 'test 25', 'test 26'], ['test 21', 'test 22', 'test 23', 'test 24', 'test 25', 'test 26', 'test 27'], ['test 22', 'test 23', 'test 24', 'test 25', 'test 26', 'test 27', 'test 28'], ['test 23', 'test 24', 'test 25', 'test 26', 'test 27', 'test 28', 'test 29'], ['test 24', 'test 25', 'test 26', 'test 27', 'test 28', 'test 29', 'test 30']]
    :param p_sheet_id:
    :return:
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials_Google_Sheet_API_Account.json'
    creds = None
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = p_sheet_id
    # https://developers.google.com/sheets/api/quickstart/python
    service = build('sheets', 'v4', credentials=creds,cache_discovery=False)
    # Call the Sheets API
    sheet = service.spreadsheets()
    try:
        """
        https://stackoverflow.com/a/51852293/10551444
        This sample retrieves the sheet name, the number of last row and last column of data range using sheet index. When 0 is used for the sheet index, it means the first sheet.
        """
        res = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, fields='sheets(data/rowData/values/userEnteredValue,properties(index,sheetId,title))').execute()
        sheetIndex = 0
        sheetName = res['sheets'][sheetIndex]['properties']['title']
        lastRow = len(res['sheets'][sheetIndex]['data'][0]['rowData'])
        lastColumn = max([len(e['values']) for e in res['sheets'][sheetIndex]['data'][0]['rowData'] if e])
        # ==================================================
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=f"{sheetName}!a1:{lastColumn}{lastRow}").execute()
        values = result.get('values', [])
        print(values)
        if not values:
            print('No data found.')
            return None
        else:
            return values
    except Exception as ex:
        print(f"ERROR : {ex}")
        if str(ex).find("HttpError 403")!=-1:
            PopupMessage("Error Google Sheet!",f"Please share for everyone the Google sheet : {ex}",f"https://docs.google.com/spreadsheets/d/{SAMPLE_SPREADSHEET_ID}")
            return None


def GoogleSheetAddValues(p_sheet_id,p_list_values):
    """
    This function go to Google sheet and Add t a row of values.
    :param p_sheet_id:
    :return:
    """
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials_Google_Sheet_API_Account.json'
    creds = None
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = p_sheet_id
    # https://developers.google.com/sheets/api/quickstart/python
    service = build('sheets', 'v4', credentials=creds,cache_discovery=False)
    # Call the Sheets API
    sheet = service.spreadsheets()

    try:
        """
        https://stackoverflow.com/a/51852293/10551444
        This sample retrieves the sheet name, the number of last row and last column of data range using sheet index. When 0 is used for the sheet index, it means the first sheet.
        """
        res = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                         fields='sheets(data/rowData/values/userEnteredValue,properties(index,sheetId,title))').execute()
        sheetIndex = 0
        sheetName = res['sheets'][sheetIndex]['properties']['title']
        # === We need to check if there are some values or not in the spreadsheet
        values_spreadsheet = GoogleSheetGetValues(p_sheet_id)
        print(f"values_spreadsheet : {values_spreadsheet}")
        if values_spreadsheet:
            try:
                lastRow = len(res['sheets'][sheetIndex]['data'][0]['rowData'])
                lastColumn = max([len(e['values']) for e in res['sheets'][sheetIndex]['data'][0]['rowData'] if e])

                # ==================================================
                # The A1 notation of a range to search for a logical table of data.
                # Values will be appended after the last row of the table.
                range_ = f"{sheetName}!A{lastRow}"  # TODO: Update placeholder value.
            except Exception as ex:
                print(f"Error : {ex}")
        else:
            range_ = f"{sheetName}!a1"
        value_range_body = {
                              "majorDimension": "ROWS",
                              "values": [p_list_values]
                            }
        request = service.spreadsheets().values().append(spreadsheetId=p_sheet_id, range=range_, valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS', body=value_range_body)
        response = request.execute()
        # TODO: Change code below to process the `response` dict:
        print(response)
        return True
    except Exception as ex:
        print(f"ERROR : {ex}")
        if str(ex).find("HttpError 403")!=-1:
            PopupMessage("Error Google Sheet!",f"Please share for everyone the Google sheet : {ex}",f"https://docs.google.com/spreadsheets/d/{SAMPLE_SPREADSHEET_ID}")
            return False


 # EXEMPLES CODES SQLITE3 PYTHON

# ===================== DATABASES ===========================
# PLEASE WATCH https://www.youtube.com/watch?v=K0zF1GiPrxY&t=2429s

def DemoSQLITE3():
     sqlite_connection = sqlite3.connect (LoadFile ('db.db'))
     sqlite_cursor = sqlite_connection.cursor ()


     # GET DATA FROM TABLE
     actions_done_last_1H_tuple = sqlite_cursor.execute ("SELECT COUNT(*) FROM actions WHERE platform LIKE ? AND  \
             id_social_account LIKE ? AND type_action LIKE ? AND date_created >?", (f"%{platform_name}%", f"%{p_username}%", f"%{string_to_search}%",one_hour_ago)).fetchall ()


     # INSERT DATA
     sqlite_cursor.execute("INSERT INTO settings(pid) VALUES(?)",(mypid,))
     sqlite_connection.commit()

     # UPDATE DATA
     sqlite_cursor.execute("UPDATE settings set pid=? WHERE id=?",(mypid, id_settings))
     sqlite_connection.commit()

# extract spreadsheet id
def extract_ss_id(spread_sheet_url):
    spread_sheet_url = spread_sheet_url.replace('https://docs.google.com/spreadsheets/d/', '')
    ind = spread_sheet_url.index('/')
    spread_sheet_url = spread_sheet_url[:ind]
    #print(spread_sheet_url)
    return spread_sheet_url

# extract spreadsheet id. uses regular expression to identify the id
def extract_ss_id_regex(spread_sheet_url):
    return re.search('/spreadsheets/d/([a-zA-Z0-9-_]+)', spread_sheet_url).group(1)


def ScrollToTheEnd(driver):
    """A method to scroll the page all the way down the bottom of the page until you can't scroll anymore."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")
    page_end = False
    while page_end == False:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            page_end = True

        last_height = new_height
                  
                  
def scrollPopup(class_name, driver):
    # Scrolls any popups. Take the popup class name as an argument
    # Simulate scrolling to capture all posts
    SCROLL_PAUSE_TIME = 3

    # Get scroll height
    js_code = "return document.getElementsByClassName('{}')[0].scrollHeight".format(class_name)
    last_height = driver.execute_script(js_code)

    while True:
        # Scroll down to bottom
        path = "//div[@class='{}']".format(class_name)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", driver.find_element_by_xpath(path))

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script(js_code)
        if new_height == last_height:
            break
        last_height = new_height                
                  
                  
 # FONCTION TO TRANSFORM AND PREPARE THE MESSAGE BEFORE TO SEND IT
def TransformMessage(msg=None, **kwargs):
    # Replaces the random text
    if not msg.__contains__("random_abc"):
        return (str(msg), "Undefined Message")[msg == '']
    random_txt_group = re.findall("{random_abc:(.*?)}", msg)
    for random_txt in random_txt_group:
        random_txt_list = random_txt.split('|')
        msg = msg.replace('{random_abc:' + random_txt + '}', random.choice(random_txt_list))
    
    # Replaces user details
    for key in kwargs:
        if msg.__contains__(key):
            place_holder = '{'+key+'}'
            #print(rpl)
            msg = msg.replace(place_holder, kwargs.get(key))
    return msg

                  
                  
                  
def TransformMessageTMP(old_message,p_firstname='',p_username=''):
    """
    This function will convert the placeholders:
        {firstname},
        {username},
        These values are in table 'contacts'

        {random_abc},
        These values are in the placeholder


        {affiliate_code},
        {affiliate_url},
        {affiliate_coupon}
        These values will be handle by us
    """

    new_message = random_abc(old_message)
    new_message = new_message.replace("""{firstname}""",p_firstname).replace("""{username}""",p_username)

    print(f"new_message : {new_message}")
    return new_message
