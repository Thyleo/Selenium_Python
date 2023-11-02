# Pour organiser le code : shift + alt + F
# Pour voir si un element est unique dans la console, la syntaxe est la suivante : $x("//nom_de_la_balise[@id/class='nom']")
# Exemple : $x("//input"[@id='name']"])
# Dans les addons (ex:ranorex), la syntaxe st : //nom_balise[@id/class='nom']
# Sur chrome, on peut egalement rechercher dans elements avec ctrl+F un element et voir les resultats (1 of 1)
# Toutes ces recherches sont facilitees par l'extension "ranorex selocity" du DevTools ou chropath
# Pour savoir si on est dans un iframe, aller dans la console et cliquer sur la fleche deroulante
# Pour identifier de facon unique un element, on peut utiliser les attributs d'une balise qui sont par exemple : id="**" type="**" name="**"
# DOM = Document Object Model est une arborescence de noeuds par exemple :
#   HTML - BODY - INPUT- etc...
#        - HEAD - etc...
# Pour ouvrir un lien via selenium :

from selenium import webdriver
import os

# https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_win32.zip : pour telecharger chromedriver


class RunChromeTests():

    def testMethod(self):

        # lancement du pilote pour chrome
        self.driverLocation = "C:\\Users\\HP\\Desktop\\THIERRY\\Stage-Python\\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = self.driverLocation
        self.driver = webdriver.Chrome(self.driverLocation)
        self.driver.get("http://www.letskodeit.com")


ChromeTest = RunChromeTests()
ChromeTest.testMethod()

# //*[@id='name'] permet d'afficher toutes les balises avec un id = name
# exemple de tag name = input
# id statique = name // id dynamique = yui_10_****** il varie lorsque on recharge la page
# On peut utiliser les css selectors pour chercher des elements, exemple : balise # ou . 'nom' le tout concatené.
# Si on a class="inputs displayed-class", ceci ne fonctionne pas input[class='displayed-class']
# mais ca oui : input[class='inputs displayed-class'] et ca aussi input.inputs.displayed-class
# En CSS, on peut utiliser balise[id/class ^='nom'] pour savoir si le mot nom est au debut de id ou de class
# Exemple : <input class ="inputs class1"> ceci marche : input[class^='inp' ou 'inputs']
# On a egalement : input[class$='class1'] pour savoir si class1 est a la fin de class
# et pour finir input[class*='class1'] pour savoir si c'est dans class (le plus pratique comme test en cas de plusieurs balises)
# CSS noeud enfant exemple fieldset>table#name

