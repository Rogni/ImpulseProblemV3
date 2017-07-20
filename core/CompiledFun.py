# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from math import *


class CompiledFun(object):
    """Single-line function from string. Support functions and constants from math.
    
    Examples:
    import CompiledFun
    CompiledFun.CompiledFun("sin(t)**2 + cos(t)**2", args=["t"])({"t": 1}) #1.0
    CompiledFun.CompiledFun("2*x1 + 3*x2", args=["x1", "x2"])({"x1": 1, "x2": 3}) #11
    """
    def __init__(self, funstr, args=[]):
        """Parse and compile new function from string
        
        funstr -- function string
        args -- variables in fuction
        """
        frmstr = funstr.replace("^","**").replace("\n","").replace(";","")
        eq = 'def compfun'+str(tuple(args)).replace("'", '') + ': return ' + frmstr
        c = compile(eq, '<string>', 'exec')
        exec(c)
        self.__fun = vars()['compfun']
        self.__str = funstr
        self.__args = args
    
    def __call__(self, args={}):
        return self.__fun(**args)
    
    def __str__(self):
        return self.__str
