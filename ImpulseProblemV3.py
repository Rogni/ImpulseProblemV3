# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from PyQt5.QtCore import (QObject, QUrl, pyqtSlot, pyqtSignal, 
pyqtProperty, QVariant, QThread)
from PyQt5.QtQml import QQmlApplicationEngine, QQmlEngine, qmlRegisterType
from PyQt5.QtWidgets import QApplication
from sys import argv
import json

from core.CompiledFunction import CompiledFunction
from core.ImpulseSystem import ImpulseSystem, arglist, result_arglist
from core.ImpulseSystemDelegate import ImpulseSystemDelegate
from core.Localization import LangManagerSingleton, LangManagerDelegate

try:
    from OpenGL import GLU
except Exception:
    pass


QML_SRC_DIR = "qmlsrc/%s"
QML_RESULT_WINDOW_URL = QML_SRC_DIR % "ResultWindow.qml"
QML_MAIN_WINDOW_URL = QML_SRC_DIR % "ImpulseSystemV3.qml"


#Errors keys
ERROR_LOAD_FILE_TITLE = "ERROR_LOAD_FILE_TITLE"
ERROR_SAVE_FILE_TITLE = "ERROR_SAVE_FILE_TITLE"
ERROR_PARSE_POINTS_TITLE = "ERROR_PARSE_POINTS_TITLE"
ERROR_PARSE_THETA_TITLE = "ERROR_PARSE_THETA_TITLE"
ERROR_PARSE_DIFF_SYS_TITLE = "ERROR_PARSE_DIFF_SYS_TITLE"
ERROR_PARSE_IMP_OPER_TITLE = "ERROR_PARSE_IMP_OPER_TITLE"
ERROR_IN_CALCULATIONS = "ERROR_IN_CALCULATIONS"


#MainView -- ToolBar Titles keys
OPEN = "OPEN"
SAVE = "SAVE"
CALCULATE = "CALCULATE"
LANG = "LANG"

#MainView -- Content Titles keys
DIFF_SYSTEM_TITLE = "DIFF_SYSTEM_TITLE"
IMPULSE_OPERATOR_TITLE = "IMPULSE_OPERATOR_TITLE"
INITIAL_POINTS_TITLE = "INITIAL_POINTS_TITLE"
THETA_LIST_TITLE = "THETA_LIST_TITLE"

#MainView -- Content lables keys
ADD = "ADD"
ADD_POINT = "ADD_POINT"

#MainView -- Dialog lables keys
MAX_TIME = "MAX_TIME"
STEP_ON_T = "STEP_ON_T"
NEW_DIMENTION = "NEW_DIMENTION"


class QMLWindowController(QObject, LangManagerDelegate):
    """
    """
    def __init__(self, urlstr, parent=None):
        super().__init__(parent)
        self.engine = QQmlApplicationEngine()
        self.engine.load(QUrl(urlstr))
        self.window = self.engine.rootObjects()[0]  
        self.window.windowClosed.connect(self.onclosing)
        LangManagerSingleton.getinstance().add_delegate(self)
        self.on_language_changed()
        
    def show_view(self):
        self.window.show()
    @pyqtSlot()
    def onclosing(self):
        LangManagerSingleton.getinstance().remove_delegate(self)

class ResultWindowController(QMLWindowController):
    def __init__(self, parent=None):
        super().__init__(QML_RESULT_WINDOW_URL, parent)
        self.window.plotResult.connect(self.drawplotresult)

    def setresult(self, args, res):
        self.__args = args
        self.__res = res
        self.window.setProperty('args', args)
        self.window.setProperty('model', res)
    
    @pyqtSlot(QVariant)
    def drawplotresult(self, args):
        import matplotlib.pyplot as mpl
        import matplotlib.backends.backend_qt5 as mplqt
        from mpl_toolkits.mplot3d import Axes3D
        mpl.rcParams["axes.grid"] = True
        if len(args.toVariant())==3:
            mpl.axes(projection='3d')
        for r in self.__res:
            pl = []
            for k in args.toVariant():
                pl.append(r[k])
            mpl.plot(*pl)
        mpl.axis('equal') 
        mplqt.show()


class MainWindowController(QMLWindowController):
    startcalc = pyqtSignal(float, float)
    error = pyqtSignal(str, str)
    calccompleted = pyqtSignal()
    
    PROP_NAME_DIM = "dim"
    PROP_NAME_DIFFSYS = "diffSysList"
    PROP_NAME_IMP_OPER = "impOperatorList"
    PROP_NAME_POINTS = "points"
    PROP_NAME_THETA = "theta"
    
    def __init__(self, parent=None):
        super().__init__(QML_MAIN_WINDOW_URL, parent)
        self.connects()
        self.__bgthread = QThread()
        self.__impsyslist = []
        self.__impulsesystemdelegate = ImpulseSystemDelegate()
    
    def connects(self):
        self.window.calculate.connect(self.startCalculated)
        self.error.connect(self.window.error)
        self.startcalc.connect(self.window.calculateStarted)
        self.calccompleted.connect(self.window.calculateFinished)
        self.window.openFile.connect(self.openFile)
        self.window.saveFile.connect(self.saveFile)
        self.window.langChanged.connect(self.lang_changed)
    
    @pyqtSlot(str)
    def lang_changed(self, langname):
        LangManagerSingleton.getinstance().setlanguageatname(langname)
    
    def setargstodelegate(self):
        self.__impulsesystemdelegate.setdata(
            dim = self.dim,
            diffsys = self.diffSysList,
            impoper = self.impOperatorList,
            points = self.points,
            thetastr = self.theta
        )

    def readdatafromdelegate(self):
        self.dim = self.__impulsesystemdelegate.dim()
        self.diffSysList = self.__impulsesystemdelegate.diffsys()
        self.impOperatorList = self.__impulsesystemdelegate.impoperator()
        self.points = self.__impulsesystemdelegate.points()
        self.theta = self.__impulsesystemdelegate.theta()

    def openFile(self, url):
        self.__impulsesystemdelegate.fileurl = url
        title = LangManagerSingleton.localization()[ERROR_LOAD_FILE_TITLE]
        self.runblockorprinterror(self.__impulsesystemdelegate.load, title)
        self.readdatafromdelegate()
    
    def saveFile(self, url):
        self.setargstodelegate()
        self.__impulsesystemdelegate.fileurl = url
        title = LangManagerSingleton.localization()[ERROR_SAVE_FILE_TITLE]
        self.runblockorprinterror(self.__impulsesystemdelegate.save, title)
    
    @property
    def dim(self):
        return self.window.property(MainWindowController.PROP_NAME_DIM)
    @dim.setter
    def dim(self, val):
        self.window.setProperty(MainWindowController.PROP_NAME_DIM, val)
    
    @property
    def diffSysList(self):
        return self.window.property(MainWindowController.PROP_NAME_DIFFSYS).toVariant()
    @diffSysList.setter
    def diffSysList(self, val):
        self.window.setProperty(MainWindowController.PROP_NAME_DIFFSYS, val)
    
    @property
    def impOperatorList(self):
        return self.window.property(MainWindowController.PROP_NAME_IMP_OPER).toVariant()
    @impOperatorList.setter
    def impOperatorList(self, val):
        self.window.setProperty(MainWindowController.PROP_NAME_IMP_OPER, val)
    
    @property
    def points(self):
        return self.window.property(MainWindowController.PROP_NAME_POINTS).toVariant()
    @points.setter
    def points(self, val):
        self.window.setProperty(MainWindowController.PROP_NAME_POINTS, val)
    
    @property
    def theta(self):
        return self.window.property(MainWindowController.PROP_NAME_THETA).toVariant()
    @theta.setter
    def theta(self, val):
        self.window.setProperty(MainWindowController.PROP_NAME_THETA, val)
    
    def runblockorprinterror(self, block, errortitle):
        try:
            block()
            return True
        except Exception as ex:
            print(str(ex))
            self.error.emit(errortitle, str(ex))
            return False
    
    def startCalculated(self, time, step):
        self.setargstodelegate()
        impsys = ImpulseSystem()
        impsys.dim = self.__impulsesystemdelegate.parsedim()
        def parsepoints(): 
            impsys.points = self.__impulsesystemdelegate.parsepoints()
        def parsetheta(): 
            impsys.theta = self.__impulsesystemdelegate.parsetheta()
        def parsediffsystem(): 
            impsys.diffsys = self.__impulsesystemdelegate.parsediffsystem()
        def parseimpoperator(): 
            impsys.impoperator = self.__impulsesystemdelegate.parseimpoperator()
        if not self.runblockorprinterror(parsepoints, 
            LangManagerSingleton.localization()[ERROR_PARSE_POINTS_TITLE]): 
            return
        if not self.runblockorprinterror(parsetheta, 
            LangManagerSingleton.localization()[ERROR_PARSE_THETA_TITLE]): 
            return
        if not self.runblockorprinterror(parsediffsystem, 
            LangManagerSingleton.localization()[ERROR_PARSE_DIFF_SYS_TITLE]): 
            return
        if not self.runblockorprinterror(parseimpoperator, 
            LangManagerSingleton.localization()[ERROR_PARSE_IMP_OPER_TITLE]): 
            return
        self.addsystobgthread(impsys)
        self.__bgthread.start()
        self.startcalc.emit(time, step)
    
    @pyqtSlot(QObject, str)
    def errorcalc(self, impsys, msg):
        self.error.emit(LangManagerSingleton.localization()[ERROR_IN_CALCULATIONS], msg)
        self.__impsyslist.remove(impsys)
        del(impsys)
        if len(self.__impsyslist) == 0:
            self.__bgthread.quit()
    
    def addsystobgthread(self, impsys):
        self.startcalc.connect(impsys.startcalc)
        impsys.calccompleted.connect(self.calccomleted)
        impsys.errorcalc.connect(self.errorcalc)
        impsys.moveToThread(self.__bgthread)
        self.__impsyslist.append(impsys)
    
    def removesysfrombgthread(self, impsys):
        self.startcalc.disconnect(impsys.startcalc)
        impsys.calccompleted.disconnect(self.calccomleted)
        impsys.errorcalc.disconnect(self.errorcalc)
        self.__impsyslist.remove(impsys)
        if len(self.__impsyslist) == 0:
            self.__bgthread.quit()
    
    @pyqtSlot(QObject)
    def calccomleted(self, impsys):
        self.r = ResultWindowController()
        args = result_arglist(impsys.dim)
        self.r.setresult(args, impsys.results)
        self.removesysfrombgthread(impsys)
        #import sys
        #print(sys.getrefcount(impsys))
        self.r.show_view()
        self.calccompleted.emit()

    #Lang manager delegate
    def on_language_changed(self):
        self.window.setProperty("calculateTitleText",
            LangManagerSingleton.localization()[CALCULATE])
        self.window.setProperty("openFileTitleText",
            LangManagerSingleton.localization()[OPEN])
        self.window.setProperty("saveFileTitleText",
            LangManagerSingleton.localization()[SAVE])
        self.window.setProperty("languageText",
            LangManagerSingleton.localization()[LANG])
            

        # Content Titles
        self.window.setProperty("diffSystemTitleText",
            LangManagerSingleton.localization()[DIFF_SYSTEM_TITLE])
        self.window.setProperty("impOperatorTitleText",
            LangManagerSingleton.localization()[IMPULSE_OPERATOR_TITLE])
        self.window.setProperty("initialPoinsTitleText",
            LangManagerSingleton.localization()[INITIAL_POINTS_TITLE])
        self.window.setProperty("thetaListTitleText",
            LangManagerSingleton.localization()[THETA_LIST_TITLE])

        # Content lables
        self.window.setProperty("addText",
            LangManagerSingleton.localization()[ADD])
        self.window.setProperty("addPointText",
            LangManagerSingleton.localization()[ADD_POINT])

        # Dialog lables
        self.window.setProperty("maxTimeText", 
            LangManagerSingleton.localization()[MAX_TIME])
        self.window.setProperty("stepForTText",
            LangManagerSingleton.localization()[STEP_ON_T])
        self.window.setProperty("newDimentionText",
            LangManagerSingleton.localization()[NEW_DIMENTION])
        self.window.setProperty("currentLang",
            LangManagerSingleton.getinstance().langname())
        self.window.setProperty("langs",
            LangManagerSingleton.getinstance().all_langs())



def main():
    qApp = QApplication(argv)
    isys = ImpulseSystem()
    mwc = MainWindowController()
    mwc.show_view()
    exit(qApp.exec_())
    

if __name__=='__main__':
    main()
