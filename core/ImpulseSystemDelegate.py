# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from PyQt5.QtCore import QUrl

from core.CompiledFunction import CompiledFunction
from core.ImpulseSystem import System
import json

ERROR_THETA_MUST_ABOVE_ZERO = "ERROR_THETA_MUST_ABOVE_ZERO"

PROP_NAME_DIM = "dim"
PROP_NAME_DIFFSYS = "diffsys"
PROP_NAME_IMP_OPER = "impoper"
PROP_NAME_POINTS = "points"
PROP_NAME_THETA = "thetastr"

class ImpulseSystemDelegate(object):
    """Load, save and parse impulse sytem."""
    
    
    def __init__(self, **args):
        self.fileurl = ''
        self.__systemdict = args
    
    def setdata(self, **args):
        self.__systemdict = args
    
    def data(self):
        return self.__systemdict
    
    def load(self):
        with open(QUrl(self.fileurl).toLocalFile(), "r") as impsysfile:
            jsonstr = impsysfile.read()
            self.__systemdict = json.loads(jsonstr)
        
    def save(self):
        with open(QUrl(self.fileurl).toLocalFile(), "w") as impsysfile:
            jsonstr = json.dumps(self.__systemdict)
            impsysfile.write(jsonstr)
    
    def parsedim(self):
        return int(self.__systemdict[PROP_NAME_DIM])
    
    def parsesystematkey(self, key):
        system = System()
        system.dim = self.parsedim()
        for i in self.__systemdict[key]:
            system[int(i['index'])] = i['right']
        return system
    
    def parsediffsystem(self):
        return self.parsesystematkey(PROP_NAME_DIFFSYS)
    
    def parseimpoperator(self):
        return self.parsesystematkey(PROP_NAME_IMP_OPER)
    
    def parsepoints(self):
        strpoints = self.__systemdict[PROP_NAME_POINTS]
        fpoints = []
        for point in strpoints:
            fpoint = {}
            for k in point:
                fu = CompiledFunction(point[k], []) 
                fpoint[k] = fu({})
            fpoints.append(fpoint)
        return fpoints
    
    def parsetheta(self):
        theta = []
        for th in self.__systemdict[PROP_NAME_THETA]:
            fu = CompiledFunction(th, [])
            val = fu()
            if val > 0:
                theta.append(val)
            else:
                raise Exception(LangManagerSingleton.localization()[ERROR_THETA_MUST_ABOVE_ZERO] % (th , str(val)))
        return theta
    
    def dim(self):
        return self.__systemdict[PROP_NAME_DIM]
        
    def diffsys(self):
        return self.__systemdict[PROP_NAME_DIFFSYS]
        
    def impoperator(self):
        return self.__systemdict[PROP_NAME_IMP_OPER]
        
    def points(self):
        return self.__systemdict[PROP_NAME_POINTS]
        
    def theta(self):
        return self.__systemdict[PROP_NAME_THETA]
