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

from core.CompiledFun import CompiledFun
from core.ImpulseSystem import ImpulseSystem, System, arglist, result_arglist
from core.Localization import LangManagerSingleton

try:
    from OpenGL import GLU
except Exception:
    pass


QML_SRC_DIR = "qmlsrc/%s"
QML_RESULT_WINDOW_URL = QML_SRC_DIR % "ResultWindow.qml"
QML_MAIN_WINDOW_URL = QML_SRC_DIR % "ImpulseSystemV3.qml"

        
class ImpulseSystemDelegate(object):
    """
    """
    
    PROP_NAME_DIM = "dim"
    PROP_NAME_DIFFSYS = "diffsys"
    PROP_NAME_IMP_OPER = "impoper"
    PROP_NAME_POINTS = "points"
    PROP_NAME_THETA = "thetastr"
    def __init__(self, **args):
        self.fileurl = ''
        self.__systemdict = args
    
    def setdata(self, **args):
        self.__systemdict = args
    
    def data(self):
        return self.__systemdict
    
    def load(self):
        impsysfile = open(QUrl(self.fileurl).toLocalFile(), "r")
        jsonstr = impsysfile.read()
        impsysfile.close()
        self.__systemdict = json.loads(jsonstr)
        
    def save(self):
        impsysfile = open(QUrl(self.fileurl).toLocalFile(), "w")
        jsonstr = json.dumps(self.__systemdict)
        impsysfile.write(jsonstr)
        impsysfile.close()
    
    def parsedim(self):
        return int(self.__systemdict[self.PROP_NAME_DIM])
    
    def parsesystematkey(self, key):
        system = System()
        system.dim = self.parsedim()
        for i in self.__systemdict[key]:
            system[int(i['index'])] = i['right']
        return system
    
    def parsediffsystem(self):
        return self.parsesystematkey(self.PROP_NAME_DIFFSYS)
    
    def parseimpoperator(self):
        return self.parsesystematkey(self.PROP_NAME_IMP_OPER)
    
    def parsepoints(self):
        strpoints = self.__systemdict[self.PROP_NAME_POINTS]
        fpoints = []
        for point in strpoints:
            fpoint = {}
            for k in point:
                fu = CompiledFun(point[k], []) 
                fpoint[k] = fu({})
            fpoints.append(fpoint)
        return fpoints
    
    def parsetheta(self):
        theta = []
        for th in self.__systemdict[self.PROP_NAME_THETA]:
            fu = CompiledFun(th, [])
            val = fu()
            if val > 0:
                theta.append(val)
            else:
                raise Exception(LangManagerSingleton.localization().ERROR_THETA_MUST_ABOVE_ZERO % (th , str(val)))
        return theta
    
    def dim(self):
        return self.__systemdict[self.PROP_NAME_DIM]
        
    def diffsys(self):
        return self.__systemdict[self.PROP_NAME_DIFFSYS]
        
    def impoperator(self):
        return self.__systemdict[self.PROP_NAME_IMP_OPER]
        
    def points(self):
        return self.__systemdict[self.PROP_NAME_POINTS]
        
    def theta(self):
        return self.__systemdict[self.PROP_NAME_THETA]

class QMLWindowController(QObject):
    """
    """
    def __init__(self, urlstr, parent=None):
        super().__init__(parent)
        self.engine = QQmlApplicationEngine()
        self.engine.load(QUrl(urlstr))
        self.window = self.engine.rootObjects()[0]
    def show_view(self):
        self.window.show()


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
        title = LangManagerSingleton.localization().ERROR_LOAD_FILE_TITLE
        self.runblockorprinterror(self.__impulsesystemdelegate.load, title)
        self.readdatafromdelegate()
    
    def saveFile(self, url):
        self.setargstodelegate()
        self.__impulsesystemdelegate.fileurl = url
        title = LangManagerSingleton.localization().ERROR_SAVE_FILE_TITLE
        self.runblockorprinterror(self.__impulsesystemdelegate.save, title)
    
    @property
    def dim(self):
        return self.window.property(self.PROP_NAME_DIM)
    @dim.setter
    def dim(self, val):
        self.window.setProperty(self.PROP_NAME_DIM, val)
    
    @property
    def diffSysList(self):
        return self.window.property(self.PROP_NAME_DIFFSYS).toVariant()
    @diffSysList.setter
    def diffSysList(self, val):
        self.window.setProperty(self.PROP_NAME_DIFFSYS, val)
    
    @property
    def impOperatorList(self):
        return self.window.property(self.PROP_NAME_IMP_OPER).toVariant()
    @impOperatorList.setter
    def impOperatorList(self, val):
        self.window.setProperty(self.PROP_NAME_IMP_OPER, val)
    
    @property
    def points(self):
        return self.window.property(self.PROP_NAME_POINTS).toVariant()
    @points.setter
    def points(self, val):
        self.window.setProperty(self.PROP_NAME_POINTS, val)
    
    @property
    def theta(self):
        return self.window.property(self.PROP_NAME_THETA).toVariant()
    @theta.setter
    def theta(self, val):
        self.window.setProperty(self.PROP_NAME_THETA, val)
    
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
            LangManagerSingleton.localization().ERROR_PARSE_POINTS_TITLE): 
            return
        if not self.runblockorprinterror(parsetheta, 
            LangManagerSingleton.localization().ERROR_PARSE_THETA_TITLE): 
            return
        if not self.runblockorprinterror(parsediffsystem, 
            LangManagerSingleton.localization().ERROR_PARSE_DIFF_SYS_TITLE): 
            return
        if not self.runblockorprinterror(parseimpoperator, 
            LangManagerSingleton.localization().ERROR_PARSE_IMP_OPER_TITLE): 
            return
        self.addsystobgthread(impsys)
        self.__bgthread.start()
        self.startcalc.emit(time, step)
    
    @pyqtSlot(QObject, str)
    def errorcalc(self, impsys, msg):
        self.error.emit(LangManagerSingleton.localization().ERROR_IN_CALCULATIONS, msg)
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
    
    @pyqtSlot(QObject)
    def calccomleted(self, impsys):
        self.r = ResultWindowController()
        args = result_arglist(impsys.dim)
        self.r.setresult(args, impsys.results)
        self.r.show_view()
        self.calccompleted.emit()
        self.__impsyslist.remove(impsys)
        del(impsys)
        if len(self.__impsyslist) == 0:
            self.__bgthread.quit()


def main():
    qApp = QApplication(argv)
    isys = ImpulseSystem()
    mwc = MainWindowController()
    mwc.show_view()
    exit(qApp.exec_())
    

if __name__=='__main__':
    main()
