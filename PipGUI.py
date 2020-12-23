from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import urllib
from urllib import parse
from urllib import request
import requests
import sys
import time
import threading


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.States = ["running","fetching""installing""uninstalling"]
        self.currentState = "running"






    def setUI(self):
        self.setStyleSheet(open('styling.qss', 'r').read())
        self.baseUrl = 'https://pypi.org/pypi/' #datayı cekecegimiz sayfa
        #self.searchurl = 'https://pypi.org/search/?q=' #sayfanın arama kısmı
        self.tabWidget = QTabWidget()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'} #bağlantının engellenmemesi için kullanılan user agent
        self.messageBox = QMessageBox(QMessageBox.Information,"text","text")
        self.messageBox.setStandardButtons(QMessageBox.Ok)

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
        buttonlay=QVBoxLayout()

        Iwidget.setLayout(Mainbox)
        Mainbox.addLayout(hbox1)
        Mainbox.addLayout(hbox2)

        self.searchBox =QLineEdit()
        self.searchBox.setPlaceholderText("Paket ismi girin :")

        self.searchButton = QPushButton("PyPI'dan paket bul")
        self.downloadButton  = QPushButton("İndir")
        self.translateButton = QPushButton("Çevir")

        self.IListInfo =QTextEdit()
        self.IListInfo.setFrameStyle(0)
        self.IListInfo.setReadOnly(True)
        self.IListInfo.setFixedHeight(300)


        self.translateButton.clicked.connect(lambda : self._translate())
        self.downloadButton.clicked.connect(lambda : self._downloadPackage())
        self.searchBox.returnPressed.connect(lambda: self._searchQuery(self.searchBox))
        self.searchButton.clicked.connect(lambda: self._searchQuery(self.searchBox))


        buttonlay.addWidget(self.translateButton)
        buttonlay.addWidget(self.downloadButton)
        hbox1.addWidget(self.searchBox)
        hbox1.addWidget(self.searchButton)
        hbox2.addWidget(self.IListInfo)
        hbox2.addLayout(buttonlay)



        Iwidget.setFixedHeight(400)
        Iwidget.setFixedWidth(600)

        return Iwidget
    def _setLpackage(self):
        Lwidget = QWidget()
        hbox1 = QHBoxLayout()
        vbox1 =QVBoxLayout()

        Lwidget.setLayout(hbox1)



        self.ListBox = QListWidget()
        self.ListBox.setFixedWidth(200)
        self.ListBox.setFixedHeight(350)

        self.PListInfo = QTextEdit()
        self.PListInfo.setReadOnly(True)
        self.PListInfo.setFrameStyle(0)
        self.PListInfo.setFixedWidth(350)
        self.PListInfo.setFixedHeight(300)

        self.uninstallButton= QPushButton("Kaldır")
        self.uninstallButton.setEnabled(0)

        hbox1.addWidget(self.ListBox)
        hbox1.addLayout(vbox1)
        vbox1.addWidget(self.PListInfo)
        vbox1.addWidget(self.uninstallButton)

        self.ListBox.itemClicked.connect(lambda: self._listItemClicked())
        self.uninstallButton.clicked.connect(self._uninstallPackage)

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

        self.uninstallButton.setEnabled(1)
        packageName = self.ListBox.currentItem().text()
        jsonDataUrl = self.baseUrl + urllib.parse.quote(
               packageName) + "/json"  # lineedit'e yazılan değere göre sitede arama yapıyoruz
        packageURL = "https://pypi.org/project/" + packageName + "/"
        self.dPackageDict['Json page']=jsonDataUrl
        self.dPackageDict['PyPI page'] = packageURL
        self.dPackageDict['isInstalled'] = True
        self._fetchPackageData()


    def _packageNotFound(self):
        self.messageBox.setWindowTitle("Hata")
        self.messageBox.setText("Paket Bulunamadı!")
        self.messageBox.setIcon(QMessageBox.Warning)
        self.messageBox.exec()
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


        self.tabWidget.setEnabled(0)
        self.download = Download(self.searchBox.text().strip())
        self.download.dSignal.connect(self.isFinished)
        self.download.start()



    def isFinished(self,val):
        self.tabWidget.setEnabled(1)
        if val == -1 :
            self.messageBox.setIcon(QMessageBox.Warning)
            self.messageBox.setWindowTitle("Yükleme Hatası")
            self.messageBox.setText("İndirme Başarısız !!!")
            self.messageBox.exec()
        elif val == 100:
            self.messageBox.setIcon(QMessageBox.Information)
            self.messageBox.setWindowTitle("Yükleme Tamamlandı")
            self.messageBox.setText("İndirme Başarılı !!!")
            self.messageBox.exec()
        elif val == -2:
            self.messageBox.setIcon(QMessageBox.Warning)
            self.messageBox.setWindowTitle("Silme Hatası")
            self.messageBox.setText("Silme Başarısız !!!")
            self.messageBox.exec()
        else:
            self.messageBox.setIcon(QMessageBox.Information)
            self.messageBox.setWindowTitle("Silme Tamamlandı")
            self.messageBox.setText("Silme Başarılı !!!")
            self.messageBox.exec()

        



    def _translate(self):
        from google_trans_new import google_translator
        try:
            ttext = str(self.dPackageDict['details'])
            translator = google_translator()
            translate_text = translator.translate(ttext,lang_src='en',lang_tgt='tr')
            self.dPackageDict['details'] = translate_text


        except Exception as e :
            print(e)

        else :
            self._writeData(False)


    def _uninstallPackage(self):
        self.tabWidget.setEnabled(0)
        self.uninstall = Uninstall(self.ListBox.currentItem().text())
        self.uninstall.usignal.connect(self.isFinished)
        self.uninstall.start()




class Download(QThread):
    def __init__(self,text):
        super(Download, self).__init__()
        self.text = text

    dSignal = pyqtSignal(int)

    def run(self):

        import subprocess

        try:

            subprocess.check_call([sys.executable, '-m', 'pip', 'install', self.text])

        except Exception as e:

            self.dSignal.emit(-1)
        else:
            self.dSignal.emit(100)


class Uninstall(QThread):
    def __init__(self,text):
        super().__init__()
        self.text = text
    usignal = pyqtSignal(int)

    def run(self):
        import subprocess

        try:

            subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', self.text])

        except Exception as e:

            self.usignal.emit(-2)
        else:
            self.usignal.emit(99)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setUI()
    window.show()
    sys.exit(app.exec())
