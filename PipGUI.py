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
        self.errorMesage = QErrorMessage()
        self.setUI()
        self.show()




    def setUI(self):
        self.setStyleSheet(open('styling.qss', 'r').read())
        self.baseUrl = 'https://pypi.org/pypi/' #datayı cekecegimiz sayfa
        #self.searchurl = 'https://pypi.org/search/?q=' #sayfanın arama kısmı
        self.tabWidget = QTabWidget()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'} #bağlantının engellenmemesi için kullanılan user agent


        self.tabWidget.addTab(self._setIpackage(),"Paket Kur")
        self.tabWidget.addTab(self._setLpackage(),"Paket Kaldır")
        self.dPackageDict = self._setInstructıonPage()
        self.setFixedWidth(600)
        self.setFixedHeight(400)
        self.setCentralWidget(self.tabWidget)
        self.setWindowTitle("Paketleri Yönet")




    def _setIpackage(self):
        Iwidget = QWidget()
        Mainbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        Iwidget.setLayout(Mainbox)
        Mainbox.addLayout(hbox1)
        Mainbox.addLayout(hbox2)
        self.searchBox =QLineEdit()
        self.searchBox.setPlaceholderText("Paket ismi girin :")
        searchButton = QPushButton("PyPI'dan paket bul")
        downloadButton  = QPushButton("İndir")
        self.IListInfo =QTextEdit()
        self.IListInfo.setFrameStyle(0)
        self.IListInfo.setReadOnly(True)
        self.IListInfo.setFixedHeight(300)
        downloadButton.clicked.connect(lambda : self._downloadPackage())
        self.searchBox.returnPressed.connect(lambda: self._searchQuery(self.searchBox))
        searchButton.clicked.connect(lambda: self._searchQuery(self.searchBox))

        hbox1.addWidget(self.searchBox)
        hbox1.addWidget(searchButton)
        hbox2.addWidget(self.IListInfo)
        hbox2.addWidget(downloadButton)


        Iwidget.setFixedHeight(400)
        Iwidget.setFixedWidth(600)

        return Iwidget
    def _setLpackage(self):
        Lwidget = QWidget()
        Mainbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        Lwidget.setLayout(Mainbox)
        Mainbox.addLayout(hbox1)
        self.ListBox = QListWidget()
        self.ListBox.setFixedWidth(200)
        self.ListBox.setFixedHeight(350)
        self.PListInfo = QTextEdit()
        self.PListInfo.setReadOnly(True)
        self.PListInfo.setFrameStyle(0)
        hbox1.addWidget(self.ListBox)
        hbox1.addWidget(self.PListInfo)
        self.ListBox.itemClicked.connect(lambda: self._listItemClicked())
        Lwidget.setFixedHeight(400)
        Lwidget.setFixedWidth(600)
        return Lwidget


    def _searchQuery(self, query):

        if query.text().strip() == "": #whitespace girilmesi ya da bir şey girilmemesi kontrolü
            self._packageNotFound()
            return
        packageName = query.text().strip().lower()
        packageURL = "https://pypi.org/project/"+packageName+"/"
        jsonDataUrl = self.baseUrl + urllib.parse.quote(
            packageName) + "/json"  # lineedit'e yazılan değere göre sitede arama yapıyoruz
        self.dPackageDict['isInstalled'] = False
        self.dPackageDict['PyPI page'] = packageURL
        self.dPackageDict['Json page'] = jsonDataUrl
        self._fetchPackageData()







    def _fetchPackageData(self):
        import  json

        try:
            req = requests.get(self.dPackageDict['Json page'], headers=self.headers)
            jsonData = req.json()

        except Exception as e:
            self._packageNotFound()
            print(e)

        else:

            self.dPackageDict['Author'] = jsonData['info']['author']
            self.dPackageDict['name'] = jsonData['info']['name']
            self.dPackageDict['version'] = jsonData['info']['version']
            self.dPackageDict['details'] = jsonData['info']['summary']
            self.dPackageDict['Homepage'] = jsonData['info']['home_page']
            self.dPackageDict['Requirements'] = jsonData['info']['requires_dist']
            for data in self.dPackageDict:

                if self.dPackageDict[data]==None:

                    self.dPackageDict[data] = ""

            self._writeData(self.dPackageDict['isInstalled'])


    def _listItemClicked(self):


        packageName = self.ListBox.currentItem().text()
        jsonDataUrl = self.baseUrl + urllib.parse.quote(
               packageName) + "/json"  # lineedit'e yazılan değere göre sitede arama yapıyoruz
        packageURL = "https://pypi.org/project/" + packageName + "/"
        self.dPackageDict['Json page']=jsonDataUrl
        self.dPackageDict['PyPI page'] = packageURL
        self.dPackageDict['isInstalled'] = True
        self._fetchPackageData()


    def _packageNotFound(self):
        self.IListInfo.setText("Package not Found !")
        return

    def _setInstructıonPage(self):
        import pkg_resources
        self.ListBox.setCurrentItem(self.ListBox.item(0))
        installed_packages = pkg_resources.working_set
        installed_packages_key_list = tuple(sorted(["%s" % (i.key)
                                          for i in installed_packages]))
        installed_packages_version_list =tuple (sorted(["%s" % (i.version)
                                              for i in installed_packages]))

        for i in installed_packages_key_list :
            self.ListBox.addItem(i)

        dPackageDict = dict(zip(installed_packages_key_list,installed_packages_version_list))
        dPackageDict['isInstalled'] = True
        return dPackageDict

    def _writeData(self, isInstalled):

        if isInstalled == True:
           pName = self.dPackageDict['name']
           try:
               tempList = pName.split("_")
           except Exception as e :
               print(e)
           else :
               pName = "-".join(tempList)
           self.PListInfo.setText(f"{str(self.dPackageDict['name']).upper()}")
           self.PListInfo.append("\n")
           self.PListInfo.append(f"İndirilen versiyon : {self.dPackageDict[pName.lower()]}")
           self.PListInfo.append("\n")
           self.PListInfo.append(f"Güncel versiyon : {self.dPackageDict['version']} ")
           self.PListInfo.append(f"Açıklama :{self.dPackageDict['details']} ")
           self.PListInfo.append(f"Anasayfa : {self.dPackageDict['Homepage']}  ")
           self.PListInfo.append(f"PyPI sayfası :{self.dPackageDict['PyPI page']} ")
           self.PListInfo.append(f"Yazar : {self.dPackageDict['Author']} ")
           self.PListInfo.append(f"Gerekli olanlar : {str(self.dPackageDict['Requirements'])}")
        else :
            self.IListInfo.setText(f"{str(self.dPackageDict['name']).upper()}")
            self.IListInfo.append("\n")
            self.IListInfo.append(f"Güncel versiyon : {self.dPackageDict['version']} ")
            self.IListInfo.append(f"Açıklama :{self.dPackageDict['details']} ")
            self.IListInfo.append(f"Anasayfa : {self.dPackageDict['Homepage']}  ")
            self.IListInfo.append(f"PyPI sayfası :{self.dPackageDict['PyPI page']} ")
            self.IListInfo.append(f"Yazar : {self.dPackageDict['Author']} ")
            self.IListInfo.append(f"Gerekli olanlar : {str(self.dPackageDict['Requirements'])}")
        return

    def _downloadPackage(self):
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install',self.searchBox.text().strip() ])
        except Exception as e :
            self.errorMesage.showMessage(str(e))





#class IPackage(QDialog) :
    #def __init__(self):
    #    super.__init__()


#class LPackage(QDialog) :

#class DowLisFun() :


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())