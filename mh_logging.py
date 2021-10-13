# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 23:40:24 2021

@author: marcu
"""

from datetime import datetime

class Logging:
    def __init__(self, parent, testing_mode = True, trace = None):
        self.p = parent
        self.log = testing_mode
        self.log_trace(self, "__init__", trace)
        return

    def log_trace(self, parent, function, trace, add = ""):
        if self.log:
            trace = {"source": None, "widget": None, "parent": None
                     } if trace is None else trace
            
            if parent is None:
                trace["function"] = function
            if type(parent) is str:
                trace["function"] = parent + "." + function
            else:
                trace["function"] = parent.__class__.__name__ + "." + function
            
            if trace["source"] == "bound event":
                trace_tuple = (datetime.now(), trace["function"], 
                               trace["widget"], trace["event"])
                prnt = "%s Called %s from widget %s and event %s." % trace_tuple
                
            elif trace["source"] == "function call":
                trace_tuple = (datetime.now(), trace["function"], 
                               trace["parent"])
                prnt = "%s Called %s from within %s." % trace_tuple
                
            elif trace["source"] == "initialise class":
                trace_tuple = (datetime.now(), parent.__class__.__name__, 
                               trace["parent"])
                prnt = "%s Initialised class %s from within %s." % trace_tuple
                
            else:
                trace_tuple = (datetime.now(), trace["function"])
                prnt = "%s Called %s without trace." % trace_tuple
                
            prnt += " %s" % add
            print(prnt)
        return

log = Logging(__name__, testing_mode = False, 
              trace = {"source": "initialise class", "parent": __name__})