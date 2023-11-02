# Toujours utiliser le xpath relatif à savoir : //balise[@id/class='nom'] et pas l'abosolu pour éviter des bugs en cas de pub
# À SAVOIR : /html/body/****/****/****/balise. EXEMPLE : Html/body/header/div/div/li[2]/a  (Li[2] c'est si on a plusieurs li
# dans la derniére div)

# On peut coupler le relatif et l'absolu pour être plus précis. EXEMPLE  : //div[@id='navbar']/div/div/ul/li[2]/a.
# NB : Le simple '/' signifie que la balise que on veut est directement à côté de son parent donc c'est plutot précis
# Tandis que le double '/' signifie que la balise est certes enfant mais pas forcement à côté du parent donc faut chercher.

# Pour être plus perfomant avec le xpath, faudrait privilégier les balises parents les plus important et toujours avec le double'/'
# EXEMPLE : " //div[@id='navbar']//ul/li[2]/a " qui est mieux que //div[@id='navbar']/div/div/ul/li[2]/a

# ATTENTION : Toujours s'assurer même en utilisant cette methode que la balise utilisée dans le xpath au debut est bien unique !!!
# En cas de présence de plusieurs balises de même nom dans un parent, pour spécifier ce que l'on veut on peut utiliser le texte
# de la balise. EXEMPLE: //div[@class='row class']//a[text()='Connecter']

# En cas de doute sur le texte de la balise on peut utiliser contains. Par EXEMPLE : //div[@class='row']//a[contains(text(),'login')]
# Il existe également avec 2 conditions (and, or). EXEMPLE : //div[@id='nom']//a[contains(text(),'sign') and contains(@class,'row')]
# EXEMPLE : //form[@class='nav']//div[contains(@class,'wrapper') and contains(@href,'call')]. A noter que on ne met pas @ pour text() !!
# Si on sait que dans la balise le texte qui nous interesse et au debut de la chaine de caratéres, on peut utiliser : starts-with
# EXEMPLE : //div[@id='nom']//a[starts-with(@class,'nav') and starts-with(text(),'hey')].
# A SAVOIR : Toujours ecrire du code le plus simple possible comme //a[@href='/sign_in'] si ca peut deja identifier cet élement.


# Pour les fonctions de base de sélénium, se reférer au document pdf du dossier stage-python.
# Pour savoir si un élément est sélectionné, on utilise element.isSelected() qui renvoie un true or false
# Pour recupérer le texte d'un élément, on peut utiliser : element.text !!
# Pour recupérer la valeur d'un attribut d'un élément (Ex: class, id, name, etc..) et on précise pour quel attribut on veut.
# Ex: <input type="text" class="row"/> ca donne element.get_attribute("class") qui va renvoyer "row"
