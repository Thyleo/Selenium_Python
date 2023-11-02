# -*- coding: utf-8 -*-

"""
Author : Heubo Thierry
Email : Heubothierry@gmail.com
Pour le test, je vous prie de créer un compte Facebook !!!
Sur certains comptes, facebook empêche que on envoie des messagess. C'est normal c'est juste que ces gens ne veulent recevoir
que des messages de leurs amis donc faut les inviter !!! C'est pas un bug du code.
"""

import logging
import sqlite3
import threading
import time
import re
import mymodulesteam
from mymodulesteam import LoadFile, all_subdirs_of, KillProgram, ChromeDriverWithProfile, FireFoxDriverWithProfile, ScrollToTheEnd, GetDetailsTaskUser
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import FirefoxProfile


# ================================ LOGGER ====================================
import pathlib
import platform
import psutil

# ================================ CLASSES NÉCÉSSAIRES POUR INTÉRAGIR AVEC LA BASE DE DONNÉES ========================== #
class DataBaseTool:

    def __init__(self, databaseFileName, lock):
        """
            La méthode __init__ permet d'initialiser la classe

            :param databaseFileName: Nom du fichier de la base de données (Ex: "db.db")
            :param lock: le thread lock
        """
        self.sqlite_connection = self.connecter(databaseFileName)
        self.sqlite_cursor = self.sqlite_connection.cursor()
        self.lock = lock

    """
    ****************************************************************************************************************
    Méthodes pour manipuler la base de données
    ****************************************************************************************************************
    """
    def connecter(self, databaseFileName):
        """
            La méthode connecter permet de connecter localement dans une base de données sous forme d'un fichier

            :param databaseFileName: Nom du fichier de la base de données (Ex: "db.db")
            :return: le pointeur sur la base de données
            :rtype: sqlite3.dbapi2.Connection
        """
        return sqlite3.connect(mymodulesteam.LoadFile(databaseFileName))

    def addLine(self, tableName, fields, values):
        """
        La méthode addLine permet d'ajouter une ligne dans la table via INSERT INTO

        :param lock: le lock
        :param tableName: le nom de la table
        :param fields: les champs
        :param values: les valeurs
        :param databaseFilename: le nom du fichier de la base de données
        :type tableName: str
        :type fields: tuple
        :type values: tuple
        :return: "True" si réussi, "False" sinon
        :rtype: bool
        """

        # insérer la ligne dans la table
        with self.lock:

            # Construction de la requête
            nbValues = len(values)
            request = "INSERT INTO " + tableName + " " + str(fields) + " VALUES(" + ("?," * nbValues)[:-1] + ")"

            # Exécution de la requête
            try:
                self.sqlite_cursor.execute(request, values)
                self.sqlite_connection.commit()
                result = returnData(True, "add line success !")
            except Exception as ex:
                result = returnData(False, ex)

            return result

    def addLineRequest(self, request, values):
        """
        La méthode addLine permet d'ajouter une ligne dans la table via INSERT INTO

        :param lock: le lock
        :param tableName: le nom de la table
        :param fields: les champs
        :param values: les valeurs
        :param databaseFilename: le nom du fichier de la base de données
        :type tableName: str
        :type fields: tuple
        :type values: tuple
        :return: "True" si réussi, "False" sinon
        :rtype: bool
        """

        # insérer la ligne dans la table
        with self.lock:
            # Exécution de la requête
            try:
                self.sqlite_cursor.execute(request, values)
                self.sqlite_connection.commit()
                result = returnData(True, "add line success !")
            except Exception as ex:
                result = returnData(False, ex)

            return result

    def addLineWithID(self, tableName, fields, values):
        """
        La méthode addLine permet d'ajouter une ligne dans la table via INSERT INTO

        :param lock: le lock
        :param tableName: le nom de la table
        :param fields: les champs
        :param values: les valeurs
        :param databaseFilename: le nom du fichier de la base de données
        :type tableName: str
        :type fields: tuple
        :type values: tuple
        :return: "id" si réussi, "-1" sinon
        :rtype: bool
        """

        # insérer la ligne dans la table
        with self.lock:

            # Construction de la requête
            nbValues = len(values)
            request = "INSERT INTO " + tableName + " " + str(fields) + " VALUES(" + ("?," * nbValues)[:-1] + ")"

            # Exécution de la requête
            try:
                self.sqlite_cursor.execute(request, values)
                self.sqlite_connection.commit()
                result = returnData(self.sqlite_cursor.lastrowid, "add line success !")
            except Exception as ex:
                result = returnData(-1, ex)

            return result

    def getLines(self, columnName, tableName, conditions = {}, options = ""):
        """
        La méthode getLines permet d'obtenir les lignes via SELECT

        :param lock: le lock
        :param columnName: le(s) nom(s) de(s) colonne(s)
        :param tableName: le nom de la table
        :param conditions: les conditions (Ex: {"id": 3, "nom": "Test"})
        :param options: les options (Ex: "ORDER BY date")
        :type columnName: str
        :type tableName: str
        :type conditions: dict
        :type options: str
        :return: Une liste contenant toutes les lignes trouvées (chaque ligne est un dictionnaire {"nomColonne1": "valeur1", ...})
        :rtype: list
        """

        # obtenir les lignes de la table
        with self.lock:

            # Construire la clause WHERE "WHERE ..."
            whereField = " WHERE " if len(conditions) != 0 else ""
            parameters = []

            for condition in conditions:
                whereField += condition + "=? AND "
                parameters.append(conditions[condition])

            whereField = whereField[:-5]

            # Construire la clause OPTION
            optionField = " " + options if (options != "") else ""

            # construction de la requête
            request = "SELECT " + columnName + " FROM " + tableName + whereField + optionField

            try:
                # Obtention des lignes
                if len(conditions) == 0 and len(options) == 0:  # Pas conditions ni options
                    rows = self.sqlite_cursor.execute(request).fetchall()
                else: # il y a conditions et/ou option
                    rows = self.sqlite_cursor.execute(request, tuple(parameters)).fetchall()

                # Conversion en une liste de dictionnaire
                columnNames = getColumnNamesOfTable(tableName)

                rowsFinal = []  # La liste finale contenant toutes les lignes
                rowDict = {}    # Le dictionnaire représentant 1 ligne
                for row in rows:
                    for nbColumns in range(len(row)):
                        rowDict[columnNames[nbColumns]] = row[nbColumns]
                    rowsFinal.append(rowDict.copy())

                result = returnData(True, rowsFinal)

            except Exception as ex:
                result = returnData(False, ex)

            return result

    def getLinesRequest(self, request, parameters = ""):
        """
            La méthode getLines permet d'obtenir les lignes via SELECT

            :param lock: le lock
            :param tableName: le nom de la table
            :param parameters: les paramètres
            :type tableName: str
            :type request: str
            :type parameters: tuple
            :return: Une liste contenant toutes les lignes trouvées (chaque ligne est un dictionnaire {"nomColonne1": "valeur1", ...})
            :rtype: list
            """

        if "WHERE" in request:
            res = re.search("(?<=FROM )[a-zA-Z .=_]+ WHERE", request)
            tableName = res.group(0)[:-6]

        else:
            res = re.search("(?<=FROM )[a-zA-Z .=_]+", request)
            tableName = res.group(0)

        # obtenir les lignes de la table
        with self.lock:
            try:
                # Obtention des lignes
                if parameters == "":  # Pas conditions ni options
                    rows = self.sqlite_cursor.execute(request).fetchall()
                else:  # il y a conditions et/ou option
                    rows = self.sqlite_cursor.execute(request, parameters).fetchall()

                # Conversion en une liste de dictionnaire
                columnNames = getColumnNamesOfTable(tableName)

                rowsFinal = []  # La liste finale contenant toutes les lignes
                rowDict = {}  # Le dictionnaire représentant 1 ligne
                for row in rows:
                    for nbColumns in range(len(row)):
                        rowDict[columnNames[nbColumns]] = row[nbColumns]
                    rowsFinal.append(rowDict.copy())

                result = returnData(True, rowsFinal)

            except Exception as ex:
                result = returnData(False, ex)

            return result

    def getLinesRequestNoDict(self, request, parameters = ""):
        """
            La méthode getLines permet d'obtenir les lignes via SELECT

            :param lock: le lock
            :param tableName: le nom de la table
            :param parameters: les paramètres
            :type tableName: str
            :type request: str
            :type parameters: tuple
            :return: Une liste contenant toutes les lignes trouvées (chaque ligne est un dictionnaire {"nomColonne1": "valeur1", ...})
            :rtype: list
            """

        # obtenir les lignes de la table
        with self.lock:
            try:
                # Obtention des lignes
                if parameters == "":  # Pas conditions ni options
                    rows = self.sqlite_cursor.execute(request).fetchall()
                else:  # il y a conditions et/ou option
                    rows = self.sqlite_cursor.execute(request, parameters).fetchall()

                result = returnData(True, rows)

            except Exception as ex:
                result = returnData(False, ex)

            return result

    def modifyLine(self, tableName, fields, values, conditions):
        """
        La méthode modifyLine permet de modifier une ligne via UPDATE

        :param lock: le lock
        :param tableName: le nom de la table
        :param fields: les champs
        :param values: les valeurs
        :param conditions: les conditions (Ex: {"id": 3, "nom": "Test"})
        :type tableName: str
        :type fields: list
        :type values: list
        :type conditions: dict
        :return: "True" si réussi, "False" sinon
        :rtype: bool
        """

        with self.lock:
            # construire la requête
            whereField = " WHERE "   # la clause de "WHERE ..."
            parameters = values.copy() # les paramètres (value1, value2, ...)
            for condition in conditions:
                whereField += condition + "=? AND "
                parameters.append(conditions[condition])

            whereField = whereField[:-5]
            parameters = tuple(parameters)

            # construire la requête
            request = "UPDATE " + tableName + " SET "

            for field in fields:
                request += field + "=?,"

            request = request[:-1]
            request += whereField

            # Exécution de la requete
            try:
                self.sqlite_cursor.execute(request, parameters)
                self.sqlite_connection.commit()
                result = returnData(True, "update line success!")
            except Exception as ex:
                result = returnData(False, ex)

            return result

    def modifyLineRequest(self, request, parameters):
        """
        La méthode modifyLine permet de modifier une ligne via UPDATE

        :param lock: le lock
        :param tableName: le nom de la table
        :param fields: les champs
        :param values: les valeurs
        :param conditions: les conditions (Ex: {"id": 3, "nom": "Test"})
        :type tableName: str
        :type fields: list
        :type values: list
        :type conditions: dict
        :return: "True" si réussi, "False" sinon
        :rtype: bool
        """

        with self.lock:
            # Exécution de la requete
            try:
                self.sqlite_cursor.execute(request, parameters)
                self.sqlite_connection.commit()
                result = returnData(True, "update line success!")
            except Exception as ex:
                result = returnData(False, ex)

            return result
def getColumnNamesOfTable(tableName):
    """
    La méthode getColumnNamesOfTable permet d'avoir les noms de tous les colonnes d'une table

    :param tableName: le nom de la table
    :type tableName: str
    :return: liste contenant les noms de tous les colonnes
    :rtype: list
    """

    sqlite_connection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))
    sqlite_cursor = sqlite_connection.cursor()

    # Effectuer une requête sur la table
    sqlite_cursor.execute("SELECT * FROM " + tableName)

    infos = sqlite_cursor.description
    columnNames = []

    for info in infos:
        columnNames.append(info[0])

    return columnNames
def returnData(ok, data):
    """
    La méthode returnData propose un format de return pour les méthodes de base de données

    :param ok: si l'operation s'est bien passée
    :type ok: bool
    :param data: le data associé a l'opération
    :type data: Any
    :return: un dictionnaire sous format {"ok": True/False, "data": "..."}
    :rtype: dict
    """

    return {"ok": ok, "data": data}
def getExceptionFormat(ex):
    return ex.__class__.__name__ + ": " + str(ex)

# ================================== INITIALISATION DU LOGGER ============================================ #
open(LoadFile("log.log"), "w").close()
logger = logging.getLogger("__Linkedin_Browser_Bot__")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s")
file_handler = logging.FileHandler(LoadFile("log.log"))
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ===================================   FONCTION D'ENVOI DE MESSAGE À UN PROFIL  ===================================== #
def send_message(driver, profile, databaseTool):
    try:
        driver.get(profile)
        btn_message = driver.find_element_by_xpath("//span[contains(text(),'Message')]")
        btn_message.click()
        msg_inputBox = driver.find_element_by_xpath("//div[@aria-label='Message' and @class='notranslate _5rpu']")
        time.sleep(3)
        add_message = "Bonjour à vous"  # LE MESSAGE À ENVOYER EST IÇI !!!
        databaseTool.addLine("actions", ("platform", "type_action", "message"),
                             ("facebook", "Group Admins", add_message))
        msg_inputBox.send_keys(add_message)
        time.sleep(3)
        sendMessage_button = driver.find_element_by_xpath(
            "//div[@class='oajrlxb2 gs1a9yip g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 goun2846 ccm00jje s44p3ltw mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv nhd2j8a9 pq6dq46d mg4g778l btwxx1t3 pfnyh3mw p7hjln8o knvmm38d cgat1ltu bi6gxh9e kkf49tns tgvbjcpo hpfvmrgz cxgpxx05 dflh9lhu sj5x9vvc scb9dxdr l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of du4w35lb lzcic4wl abiwlrkh p8dawk7l']")
        sendMessage_button.click()
        time.sleep(3)
        close_btn = driver.find_element_by_xpath("//div[contains(@aria-label,'Fermer')]")
        close_btn.click()
        time.sleep(5)
    except Exception as ex:
        logger.error(f"Error while sending message {ex}")

# =============================  OUVERTURE DE L'URL DES GROUPES ET DE LA PARTIE MEMBRES ============================== #
def urlToID(googleSheetURL):
    """
    La méthode urlToID permet d'extaire l'ID du document à partir d'un lien de Google Sheet

    :param googleSheetURL: Lien Google Sheet complet (Ex: https://docs.google.com/spreadsheets/d/1CQFoq_4WVsRTEts6szLn2HIx8w9fNgWy5UzqxbPR26o/edit?usp=sharing)
    :type googleSheetURL: str
    :return: id de Google Sheet
    :rtype: str
    """
    return googleSheetURL.split("/")[5]  # Dans l'exemple, id est "1CQFoq_4WVsRTEts6szLn2HIx8w9fNgWy5UzqxbPR26o"
def getColumnsFromGoogleSheetByURL(googleSheetURL):
    """
    La méthode getColumnsFromGoogleSheetByURL permet d'obtenir les valeurs dans les différentes colonnes de Google Sheet

    :param googleSheetURL: Lien Google Sheet complet
    :type googleSheetURL: str
    :return: Une liste contenant toutes les lignes du Google Sheet
    :rtype: list
    """
    idGoogleSheet = urlToID(googleSheetURL)  # Obtenir id de Google Sheet
    return mymodulesteam.GoogleSheetGetValues(idGoogleSheet)  # Obtenir toutes les lignes du doc
def Open_page(driver, url):

    # ============================ CHARGEMENT DE LA PAGE ================================ #
    driver.get(url[0])
    driver.maximize_window()
    driver.implicitly_wait(10)

    # ============================= ON OUVRE L'ONGLET DES MEMBRES ======================== #
    try:
        time.sleep(2)
        members_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, (
                "(//a[contains(@href, '/groups/') and contains(@href, '/members/')])[last()]")))
        )
        driver.execute_script("arguments[0].click();", members_button)
    except Exception as ex:
        logger.error(f"Error when selecting members tab: {ex}")
        return False

# =======================================         DEBUT DE LA TÂCHE                  ================================= #
def Browser_Influencers_Facebook_Group_Admins(p_browser, p_taskuser_id, Linkedin_username, p_quantity_actions, label_log, lock):
    """This functions allows to message group admins / moderators of a defined group"""
    logger.info("=============================== [1] Open Browser =======================================")

    # ==================== CHARGEMENT DE LA BASE DE DONNÉES ======================= #
    sqlite_connection = sqlite3.connect(mymodulesteam.LoadFile('db.db'))
    sqlite_cursor = sqlite_connection.cursor()
    databaseTool = DataBaseTool("db.db", lock)

    # ===================== OUVERTURE DU NAVIGATEUR ================================= #
    try:
        if p_browser == "Chrome":
            driver = ChromeDriverWithProfile()
        elif p_browser == "Firefox":
            driver = FireFoxDriverWithProfile()
        else:
            logger.error(f"PhoneBot didn't find the browser called '{p_browser}'.")
    except Exception as ex:
        logger.error(f"Error profile {ex}, YOU CAN ALSO CHECK THE FUNCTION Open_page !")

    tab_url = getColumnsFromGoogleSheetByURL(
        "https://docs.google.com/spreadsheets/d/1dDhSMSF2NdGEsnSIUBLIKGsmlD2mJWBWGi9N8Jy325A/edit?usp=sharing")
    for url in tab_url:
        try:
            Open_page(driver, url)  # OUVERTURE DES URL. LA FONCTION EST AU DEBUT DU CODE.
            time.sleep(5)

        # ============================= ON RECUPERE LES URL DES PROFILS DES ADMINS =============================== #
            try:
        # ====================== ICI, Je recupére un tableau contenant le nombre de membres et d'admins. ===================== #
                tab_number = WebDriverWait(driver, 12).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, (
                         "//span[contains(@class,'d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh jq4qci2q a3bd9o3v knj5qynh m9osqain')]//strong"))
                    )
                )
        # ============================== ICI, JE SEPARE NOMBRE DE MEMBRES DE NOMBRES D'ADMINS ================================== #
        # ================ ET J'ENLEVE LES ESPACES POUR OBTENIR UN NOMBRE QUI EST LE NOMBRE D'ADMINS =========================== #
                len_String = len(tab_number[1].text.replace(" ", ""))
                number_admins = tab_number[1].text.replace(" ", "")[1:len_String]
                print("Le nombre d'admins de ce groupe est de : "+ number_admins)
                time.sleep(2)

        # ====================  ICI, JE VÉRIFIE SI LE NOMBRE D'ADMINS EST > 10 ET SI OUI JE CLIQUE SUR AFFICHER TOUS LE ADMINS ================ #
                if int(number_admins) > 10:
                    see_allButton = driver.find_element_by_xpath("//a[contains(@href, '/admins/')]")
                    see_allButton.click()
                    ScrollToTheEnd(driver)
                    time.sleep(5)

        # ================================== ICI, JE RECUPÉRE TOUS LES MEMBRES DU GROUPE ========================================== #
                tab_members = WebDriverWait(driver, 12).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, (
                            "//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p']"))
                    )
                )
                for i in range(len(tab_members)):
                    print(tab_members[i].text)

                admins_profiles = []
                admins_profiles_url = []
        # ========================== C'EST ICI QUE À PARTIR DU NOMBRE D'ADMINS, JE RECUPÉRE UNIQUEMENT ============================ #
        # ========================== DANS LE TABLEAU DE MEMBRES LES n PREMIERS QUI SERONT LES ADMINS ============================= #
                for index in range(int(number_admins)):
                    admins_profiles.append(tab_members[index + 1].text)
                    admins_profiles_url.append(tab_members[index + 1].get_attribute("href"))
                    databaseTool.addLine("contacts", ("platform", "username"),
                                         ("facebook", admins_profiles[index]))
            except Exception as ex:
                logger.error(f"Error while waiting and getting profiles url: {ex}")
                return False

            TaskIsDone = False
            while TaskIsDone == False:
                for profile in admins_profiles_url:
        # ========================== ON ENVOIE LE MESSAGE ICI. LA FONCTION EST AU DÉBUT DU CODE !!!   ======================== #
                        send_message(driver,profile,databaseTool)
                TaskIsDone = True

        except Exception as ex:
            logger.error(f"Error while opening the URL: {ex}")
    print("Finsished. The task is done. /n The end...")
    time.sleep(30) # FIN DU CODE ICI !!!!!!!!!!!!!

p_browser = "Chrome"
p_taskuser_id = "254"
p_driver = ""
Linkedin_username = ""
p_quantity_actions = ""
label_log = ""
lock = threading.Lock()

Browser_Influencers_Facebook_Group_Admins(p_browser, p_taskuser_id, Linkedin_username, p_quantity_actions, label_log, lock)