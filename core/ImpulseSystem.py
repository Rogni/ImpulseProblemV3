# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from .CompiledFunction import CompiledFunction
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


NAME_VARS_T = 't'
NAME_VARS_THETA = 'T'
NAME_VARS_X_I = 'x%d'
NAME_NORMA = 'norma'

DEFAULT_SYSTEM_STRING = "0"

def xarglist(dim):
    """Create default point variables x1, ..., xn frome 1 to dim.
    Example:
    xarglist(3) #['x1', 'x2', 'x3']
    """
    return [NAME_VARS_X_I%(i+1) for i in range(dim)]

def arglist(dim):
    """Create default variables in impulse system"""
    return [NAME_VARS_T] + xarglist(dim) + [NAME_VARS_THETA]
            
def result_arglist(dim):
    return arglist(dim) + [NAME_NORMA]

class System(object):
    """System of equations. 
    x1 = f(t, x1,..., xn, T),
    ...,
    xn = f(t, x1,..., xn, T)
    """
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
            self.__funcs = [CompiledFunction(DEFAULT_SYSTEM_STRING, self.__args) for i in range(self.dim)]
    
    def __setitem__(self, index, strfun):
        try:
            c = CompiledFunction(strfun, self.__args)
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


class Result(object):
    """
    """
    
    
    def __init__(self, dim, args):
        self.dim = dim
        self.__args = args
        self.__reluts = {k: [] for k in args}
        self.__reluts[NAME_NORMA] = []
        pass
    
    def push_point(self, point):
        for k in self.__args:
            self.__reluts[k].append(point[k])
        self.__reluts[NAME_NORMA].append(self.norma(point))
    
    def __getitem__(self, key):
        return {i: self.__reluts[key][i] for i in self.__args}
        
    def dict(self):
        return self.__reluts
    
    def norma(self, point):
        n = 0
        args = xarglist(self.dim)
        for a in args:
            n += point[a]**2
        return n**(1/2)
    

class ThetaIter(object):
    """
    """
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
    
    def nextval(self):
        return self.__nextval

    def nexttheta(self):
        return self.__theta[self.__index]

    def searchinitindex(self, t):
        while t < self.__nextval:
            self.prev()
        while t >= self.__nextval:
            self.next()


class ImpulseSystem(QObject):
    """
    """
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
        
    @property
    def dim(self):
        return self.__dim
        
    @dim.setter
    def dim(self, dim):
        if dim > 0:
            self.__diffsys.dim = dim
            self.__impoperator.dim = dim
            self.__dim = dim

    @property
    def diffsys(self):
        return self.__diffsys
    
    @diffsys.setter
    def diffsys(self, val):
        self.__diffsys = val
    
    @property
    def impoperator(self):
        return self.__impoperator
    
    @impoperator.setter
    def impoperator(self, val):
        self.__impoperator = val
    
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
        t = point[NAME_VARS_T]
        if len(self.theta) == 0:
            self.theta = [maxtime+step]
        thetaiter = ThetaIter(self.theta)
        thetaiter.searchinitindex(t)
        p =  point.copy()
        p[NAME_VARS_THETA] = thetaiter.nexttheta()
        res = Result(self.dim, tuple(p.keys()))
        res.push_point(p)
        while t < maxtime:
            if t+step >= thetaiter.nextval():
                _h = thetaiter.nextval() - t
                p = self.nextpoint(p, _h)
                res.push_point(p)
                p = self.__impoperator(p)
                thetaiter.next()
                p[NAME_VARS_THETA] = thetaiter.nexttheta()
                res.push_point(p)
            else:
                p = self.nextpoint(p, step)
                res.push_point(p)
            t = p[NAME_VARS_T]
        return res.dict()
    
    def nextpoint(self, point, step):
        k1 = self.__diffsys(point)
        k2 = self.__diffsys(self.modifpoint(point, step/2, k1))
        k3 = self.__diffsys(self.modifpoint(point, step/2, k2))
        k4 = self.__diffsys(self.modifpoint(point, step, k3))
        p = point.copy()
        p[NAME_VARS_T] += step
        for i in xarglist(self.dim):
            p[i] = p[i] + step/6 * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        return p
    
    def modifpoint(self, point, h, k):
        p = point.copy()
        p[NAME_VARS_T] += h
        for i in xarglist(self.dim):
            p[i] = p[i] + h*k[i]
        return p
