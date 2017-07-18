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
from PyQt5.QtQml import QQmlApplicationEngine, QQmlEngine, qmlRegisterType, QJSValue
from PyQt5.QtWidgets import QApplication
from math import *
from sys import argv


try:
    from OpenGL import GLU
except Exception:
    pass


def xarglist(dim):
    return ['x'+str(i+1) for i in range(dim)]

def arglist(dim):
    return ['t'] + xarglist(dim) + ['T']

class CompiledFun:
    def __init__(self, funstr, args=['x1']):
        frmstr = funstr.replace("^","**").replace("\n","").replace(";","")
        eq = 'def compfun'+str(tuple(args)).replace("'", '') + ': return ' + frmstr
        c = compile(eq, '<string>', 'exec')
        exec(c)
        self.__fun = vars()['compfun']
        self.__str = funstr
        self.__args = args
    
    def __call__(self, argv):
        return self.__fun(**argv)
    
    def __str__(self):
        return self.__str


class ThetaIter:
    def __init__(self, thetalist):
        self.__index = 0
        self.__nextval = thetalist[0]
        self.__theta = thetalist

    def next(self):
        self.__index = self.__index + 1 if self.__index != len(self.__theta) - 1 else 0
        self.__nextval += self.__theta[self.__index]
    
    def prev(self):
        self.__index = self.__index - 1 if self.__index else len(self.__theta) - 1
        self.__nextval -= self.__theta[self.__index]
        pass
    
    def nextval(self):
        return self.__nextval

    def nexttheta(self):
        return self.__theta[self.__index]

    def searchinitindex(self, t):
        while t < self.__nextval:
            self.prev()
        while t >= self.__nextval:
            self.next()
        pass

    pass


class System:
    def __init__(self):
        self.dim = 1
        pass
    
    @property
    def dim(self):
        return self.__dim
        
    @dim.setter
    def dim(self, dim):
        if dim > 0:
            self.__dim = dim
            self.__args = arglist(dim)
            self.__funcs = [CompiledFun("0", self.__args) for i in range(self.dim)]
    
    def __setitem__(self, index, strfun):
        try:
            c = CompiledFun(strfun, self.__args)
            self.__funcs[index] = c
        except Exception as ex:
            print(ex)
        
    def __getitem__(self, index):
        return str(self.__funcs[index])

    def __call__(self, argv):
        p = argv.copy()
        xargs = xarglist(self.dim)
        for i in range(self.dim):
            p[xargs[i]] = self.__funcs[i](argv)
        return p


class Result:
    def __init__(self, dim, args):
        self.dim = dim
        self.__args = args
        self.__reluts = {k: [] for k in args}
        self.__reluts['norma'] = []
        pass
    
    def push_point(self, point):
        for k in self.__args:
            self.__reluts[k].append(point[k])
        self.__reluts['norma'].append(self.norma(point))
    
    def __getitem__(self, key):
        return {i: self.__reluts[key][i] for i in self.__args}
        
    def valueOf(self, key): 
        self[key]
    
    def dict(self):
        return self.__reluts
    
    def norma(self, point):
        n = 0
        args = xarglist(self.dim)
        for a in args:
            n += point[a]**2
        return n**(1/2)
    pass


class ImpulseSystem(QObject):
    calccompleted = pyqtSignal(QObject)
    errorcalc = pyqtSignal(QObject, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__diffsys = System()
        self.__impoperator = System()
        self.dim = 1
        self.points = []
        self.theta = []
        self.results = []
        
    @pyqtProperty(int)
    def dim(self):
        return self.__dim
        
    @dim.setter
    def dim(self, dim):
        if dim > 0:
            self.__diffsys.dim = dim
            self.__impoperator.dim = dim
            self.__dim = dim
        pass
    
    def setfuntodiffsys(self, index, fun):
        self.__diffsys[index] = fun
    
    def setfuntoimpoper(self, index, fun):
        self.__impoperator[index] = fun
    
    @pyqtSlot(float, float)
    def startcalc(self, maxtime, step):
        self.results = []
        try:
            for point in self.points:
                self.results.append(self.calcpoint(point, maxtime, step))
            self.calccompleted.emit(self)
        except Exception as ex:
            #raise ex
            self.errorcalc.emit(self, str(ex))
    
    def calcpoint(self, point, maxtime, step):
        thetaindex = 0
        t = point['t']
        if len(self.theta) == 0:
            self.theta = [maxtime+step]
        thetaiter = ThetaIter(self.theta)
        thetaiter.searchinitindex(t)
        p =  point.copy()
        p['T'] = thetaiter.nexttheta()
        res = Result(self.dim, tuple(p.keys()))
        res.push_point(p)
        while t < maxtime:
            if t+step >= thetaiter.nextval():
                _h = thetaiter.nextval() - t
                p = self.nextpoint(p, _h)
                res.push_point(p)
                p = self.__impoperator(p)
                thetaiter.next()
                p['T'] = thetaiter.nexttheta()
                res.push_point(p)
            else:
                p = self.nextpoint(p, step)
                res.push_point(p)
            t = p['t']
        return res.dict()
    
    def nextpoint(self, point, step):
        def modifpoint(point, h, k):
            p = point.copy()
            p['t'] += h
            for i in xarglist(self.dim):
                p[i] = p[i] + h*k[i]
            return p
        k1 = self.__diffsys(point)
        k2 = self.__diffsys(modifpoint(point, step/2, k1))
        k3 = self.__diffsys(modifpoint(point, step/2, k2))
        k4 = self.__diffsys(modifpoint(point, step, k3))
        p = point.copy()
        p['t'] += step
        for i in xarglist(self.dim):
            p[i] = p[i] + step/6 * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        return p


class QMLWindowController(QObject):
    def __init__(self, urlstr, parent=None):
        super().__init__(parent)
        self.engine = QQmlApplicationEngine()
        self.engine.load(QUrl(urlstr))
        self.window = self.engine.rootObjects()[0]
    def show_view(self):
        self.window.show()


class ResultWindowController(QMLWindowController):
    def __init__(self, parent=None):
        super().__init__('qmlsrc/ResultWindow.qml',parent)
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
        pass


class MainWindowController(QMLWindowController):
    startcalc = pyqtSignal(float, float)
    error = pyqtSignal(str, str)
    calccompleted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__('qmlsrc/ImpulseSystemV3.qml',parent)
        self.connects()
        self.__bgthread = QThread()
        self.__impsyslist = []
    
    def connects(self):
        self.window.calculate.connect(self.startCalculated)
        self.error.connect(self.window.error)
        self.startcalc.connect(self.window.calculateStarted)
        self.calccompleted.connect(self.window.calculateFinished)
        self.window.openFile.connect(self.openFile)
        self.window.saveFile.connect(self.saveFile)
    
    def openFile(self, url):
        import json
        try:
            u = QUrl(url)
            impsysfile = open(u.toLocalFile(), "r")
            jsonstr = impsysfile.read()
            impsysfile.close()
            
            data = json.loads(jsonstr)
            self.dim = data["dim"]
            self.diffSysList = data["diffsys"]
            self.impOperatorList = data["impoper"]
            self.points = data["points"]
            self.theta = data["thetastr"]
            
        except Exception as ex:
            self.error.emit("Ошибка при чтении файла", str(ex))
            return
    
    def saveFile(self, url):
        import json
        try:
            u = QUrl(url)
            impsysfile = open(u.toLocalFile(), "w")
            dim = self.dim
            diffsys = self.diffSysList
            impoper = self.impOperatorList
            points = self.points
            thetastr = self.theta
            data = {
                "dim": dim, 
                "diffsys": diffsys, 
                "impoper": impoper, 
                "points": points,
                "thetastr": thetastr
            }
            jsonstr = json.dumps(data)
            impsysfile.write(jsonstr)
            impsysfile.close()
        except Exception as ex:
            self.error.emit("Ошибка при записи файла", str(ex))
            return
    
    @property
    def dim(self):
        return self.window.property("dim")
    @dim.setter
    def dim(self, val):
        self.window.setProperty("dim", val)
    
    @property
    def diffSysList(self):
        return self.window.property("diffSysList").toVariant()
    @diffSysList.setter
    def diffSysList(self, val):
        print(val)
        self.window.setProperty("diffSysList", val)
    
    @property
    def impOperatorList(self):
        return self.window.property("impOperatorList").toVariant()
    @impOperatorList.setter
    def impOperatorList(self, val):
        self.window.setProperty("impOperatorList", val)
    
    @property
    def points(self):
        return self.window.property("points").toVariant()
    @points.setter
    def points(self, val):
        self.window.setProperty("points", val)
    
    @property
    def theta(self):
        return self.window.property("theta").toVariant()
    @theta.setter
    def theta(self, val):
        self.window.setProperty("theta", val)
    
    def startCalculated(self, time, step):
        dim = self.dim
        diffsys = self.diffSysList
        impoper = self.impOperatorList
        points = self.points
        thetastr = self.theta
        try:
            for point in points:
                for k in point:
                    fu = CompiledFun(point[k], []) 
                    point[k] = fu({})
        except Exception as ex:
            self.error.emit("Ошибка в начальных точках", str(ex))
            return
        theta = []
        try:
            for th in thetastr:
                fu = CompiledFun(th, [])
                theta.append(fu({}))
                pass
        except Exception as ex:
            self.error.emit("Ошибка в списке Theta", str(ex))
            return
        impsys = ImpulseSystem()
        impsys.dim = dim
        
        try:
            for i in diffsys:
                impsys.setfuntodiffsys(int(i["index"]), i["right"])
        except Exception as ex:
            self.error.emit("Ошибка в дифф системе", str(ex))
            return
        try:
            for i in impoper:
                impsys.setfuntoimpoper(int(i["index"]), i["right"])
        except Exception as ex:
            self.error.emit("Ошибка в импульсном операторе", str(ex))
            return
        impsys.points = points
        impsys.theta = theta
        
        self.addsystobgthread(impsys)
        self.__bgthread.start()
        self.startcalc.emit(time, step)
    
    @pyqtSlot(QObject, str)
    def errorcalc(self, impsys, msg):
        self.error.emit("Ошибка при вычислениях", msg)
        self.__impsyslist.remove(impsys)
        del(impsys)
        if len(self.__impsyslist) == 0:
            self.__bgthread.quit()
        pass
    
    def addsystobgthread(self, impsys):
        self.startcalc.connect(impsys.startcalc)
        impsys.calccompleted.connect(self.calccomleted)
        impsys.errorcalc.connect(self.errorcalc)
        impsys.moveToThread(self.__bgthread)
        self.__impsyslist.append(impsys)
    
    @pyqtSlot(QObject)
    def calccomleted(self, impsys):
        self.r = ResultWindowController()
        args = arglist(impsys.dim) + ['norma']
        self.r.setresult(args, impsys.results)
        self.r.show_view()
        self.calccompleted.emit()
        self.__impsyslist.remove(impsys)
        del(impsys)
        if len(self.__impsyslist) == 0:
            self.__bgthread.quit()
        pass


def main():
    app = QApplication(argv)

    isys = ImpulseSystem()
    mwc = MainWindowController()
    mwc.show_view()
    exit(app.exec_())

    pass
    

if __name__=='__main__':
    main()
