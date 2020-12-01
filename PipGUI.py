from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import urllib
from urllib import parse
from urllib import request
import requests
import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setUI()
        self.show()

    def setUI(self):
        self.baseUrl = 'https://pypi.org/pypi/' #datayı cekecegimiz sayfa
        #self.searchurl = 'https://pypi.org/search/?q=' #sayfanın arama kısmı

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'} #bağlantının engellenmemesi için kullanılan user agent
        self.setStyleSheet(open('styling.qss','r').read())
        widget = QWidget()
        v_box = QVBoxLayout()
        h_box = QHBoxLayout()
        h_box1 = QHBoxLayout()

        self.searchLine = QLineEdit("")
        self.searchLine.setPlaceholderText("Enter a package name :")
        self.searchButton = QPushButton("Find package from PyPI")
        self.listItems = QListWidget()
        self.listItems.setFixedWidth(200)
        self.listItems.setFixedHeight(300)

        self.dPackageDict = self._setInstructıonPage() #GUI ilk açıldığında gözüken sayfa

        self.sonuc = QTextEdit()
        self.sonuc.setFrameStyle(0)
        self.sonuc.setReadOnly(True)
        self.sonuc.setFixedHeight(300)
        v_box.addLayout(h_box)
        v_box.addLayout(h_box1)

        h_box.addWidget(self.searchLine)
        h_box.addWidget(self.searchButton)
        h_box1.addWidget(self.listItems)
        h_box1.addWidget(self.sonuc)

        self.searchButton.clicked.connect(lambda: self._searchQuery(self.searchLine)) #buton tıklanıldığında arama algoritması çalışır
        self.listItems.itemClicked.connect(lambda: self._listItemClicked()) #listedeki install elemanına tıklanıldığında instruction gelir


        widget.setLayout(v_box)
        widget.setFixedWidth(600)
        widget.setFixedHeight(400)
        self.setWindowTitle("Manage Packages")
        self.setCentralWidget(widget)


    def _searchQuery(self, query):

        if query.text().strip() == "": #whitespace girilmesi ya da bir şey girilmemesi kontrolü
            self._packageNotFound()
            return
        packageName = query.text().strip().lower()
        packageURL = "https://pypi.org/project/"+packageName+"/"
        jsonDataUrl = self.baseUrl + urllib.parse.quote(
            packageName) + "/json"  # lineedit'e yazılan değere göre sitede arama yapıyoruz
        packageDict = {"isInstalled": False}
        packageDict['PyPI page'] = packageURL
        packageDict['Json page'] = jsonDataUrl
        self._fetchPackageData(packageDict)







    def _fetchPackageData(self,packageDict):
        import  json

        try:
            req = requests.get(packageDict['Json page'], headers=self.headers)
            jsonData = req.json()


        except Exception as e:
            self._packageNotFound()
            print(e)



        packageDict['Author'] = jsonData['info']['author']
        packageDict['name'] = jsonData['info']['name']
        packageDict['version'] = jsonData['info']['version']
        packageDict['details'] = jsonData['info']['summary']
        packageDict['Homepage'] = jsonData['info']['home_page']
        packageDict['Requirements'] = jsonData['info']['requires_dist']
        for data in packageDict:

            if packageDict[data]==None:

                packageDict[data] = ""

        self._writeData(packageDict)








    def _listItemClicked(self):
       if self.listItems.currentItem().text() == self.listItems.item(0).text() :
           self._installClicked()
       else :
           packageName = self.listItems.currentItem().text()
           jsonDataUrl = self.baseUrl + urllib.parse.quote(
               packageName) + "/json"  # lineedit'e yazılan değere göre sitede arama yapıyoruz
           packageURL = "https://pypi.org/project/" + packageName + "/"
           self.dPackageDict['Json page']=jsonDataUrl
           self.dPackageDict['PyPI page'] = packageURL
           self._fetchPackageData(self.dPackageDict)


    def _packageNotFound(self):
        self.sonuc.setText("Package not Found !")
        return

    def _setInstructıonPage(self):
        import pkg_resources
        self.listItems.addItem("<INSTALL>")
        self.listItems.setCurrentItem(self.listItems.item(0))
        installed_packages = pkg_resources.working_set
        installed_packages_key_list = tuple(sorted(["%s" % (i.key)
                                          for i in installed_packages]))
        installed_packages_version_list =tuple (sorted(["%s" % (i.version)
                                              for i in installed_packages]))

        for i in installed_packages_key_list :
            self.listItems.addItem(i)

        dPackageDict = dict(zip(installed_packages_key_list,installed_packages_version_list))
        dPackageDict['isInstalled'] = True
        return dPackageDict







    def _installClicked(self):
        instructionText = """Install from PyPI 

                             If you don't know where to get the package from, then most likely you'll want to search the Python Package Index. 
                             Start by entering the name of the package in the search box above and pressing ENTER.


Install from requirements file

Click here to locate requirements.txt file and install the packages specified in it.

Install from local file

Click here to locate and install the package file (usually with .whl, .tar.gz or .zip extension).

Upgrade or uninstall

Start by selecting the package from the left.
"""
        self.sonuc.setText(instructionText)

    # if(q.text()==self.listItems.item(0)) :

    def _writeData(self, packageDict):


        self.sonuc.setText(f"{str(packageDict['name']).upper()}")
        self.sonuc.append("\n")
        if packageDict["isInstalled"] == True:
           pName = packageDict['name']

           self.sonuc.append(f"Installed version : {packageDict[pName.lower()]}")
           self.sonuc.append("\n")

        self.sonuc.append(f"Latest stable version : {packageDict['version']} ")
        self.sonuc.append(f"Summary :{packageDict['details']} ")
        self.sonuc.append(f"Homepage : {packageDict['Homepage']}  ")
        self.sonuc.append(f"PyPI page :{packageDict['PyPI page']} ")
        self.sonuc.append(f"Author : {packageDict['Author']} ")
        self.sonuc.append(f"Requires : {str(packageDict['Requirements'])}")
        return
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())