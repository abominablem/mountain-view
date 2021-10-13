# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 23:41:05 2021

@author: marcu
"""

from mh_logging import log

class Component:
    """
    One side of a Connection object. A Connection will have two 
    Components, an origin and a destination.
    """
    def __init__(self, xml, trace = None):
        log.log_trace(self, "__init__", trace)
        self.name = self.__class__.__name__
        self.xml = xml
        self.id = xml.attrib["ToolID"]
        self.type = xml.attrib["Connection"]
        
class Connection:  
    def __init__(self, connection_xml, trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        c = connection_xml
        self.name = c.attrib.get('name', None)
        self.wireless = (c.attrib.get('Wireless', "False") == "True")
            
        self.origin_xml = c.find("Origin")
        self.origin = Component(self.origin_xml, inf_trace)
        
        self.destination_xml = c.find("Destination")
        self.destination = Component(self.destination_xml, inf_trace)

class Connections:
    connections = []
    def __init__(self, xml, trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        
        self.xml = xml
        self.connections = self.map_connections(xml, trace = inf_trace)
        self.count = len(self.connections)
        
    def __iter__(self):
        """
        Allow iteration of node object like "for n in Connections". Equivalent 
        to doing "for n in Connections.connections"
        """
        self._i = -1
        return self
    
    def __next__(self):
        if self._i < self.count - 1:
            self._i += 1
            return self.connections[self._i]
        else:
            raise StopIteration

    def map_connections(self, xml, trace = None):
        log.log_trace(self, "map_connections", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".map_connections"}
        """
        For a given ElementTree xml object, returns a list of Connection
        objects
        """
        cnct = xml.find('Connections')
        cd = [Connection(c, trace = inf_trace) for c in cnct]
        return cd
    
    def next_node(self, node_id, trace = None):
        log.log_trace(self, "next_node", trace)
        """
        For a given node, returns a list of the node(s) that have input 
        connections from that node.
        """
        destinations = []
        for c in self.connections:
            if c.origin.id == str(node_id):
                destinations.append(c.destination)
        return destinations
    
    def previous_node(self, node_id, trace = None):
        log.log_trace(self, "previous_node", trace)
        """
        For a given node, returns a list of the node(s) that are inputs of
        that node
        """
        origins = []
        for c in self.connections:
            if c.destination.id == str(node_id):
                origins.append(c.origin)
        return origins
    
    def get_connections(self, node_id, trace = None):
        log.log_trace(self, "get_connections", trace)
        """
        For a given node, returns a list of incoming and outgoing connections
        """
        cons = []
        for c in self.connections:
            if c.origin.id == node_id or c.destination.id == node_id:
                cons.append(c)
        return cons
    
    def get_input_connections(self, node_id, trace = None):
        log.log_trace(self, "get_input_connections", trace)
        """
        For a given node, returns a list of incoming connections
        """
        cons = []
        for c in self.connections:
            if c.destination.id == node_id:
                cons.append(c)
        return cons
    
    def get_output_connections(self, node_id, trace = None):
        log.log_trace(self, "get_output_connections", trace)
        """
        For a given node, returns a list of outgoing connections
        """
        cons = []
        for c in self.connections:
            if c.origin.id == node_id:
                cons.append(c)
        return cons
    
    def is_node_multiconnection(self, node_id, trace = None):
        log.log_trace(self, "is_node_multiconnection", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".is_node_multiconnection"}
        """
        For a given node, returns a list of outgoing connections
        """
        if len(self.get_input_connections(node_id, inf_trace)) > 1:
            return True
        else:
            c_out = self.get_output_connections(node_id, inf_trace)
            types = [c.origin.type for c in c_out]
            return len(list(set(types))) > 1
        
    def remove(self, c, trace = None):
        log.log_trace(self, "is_node_multiconnection", trace)
        """
        Removes a given Connection object from self.connections
        """
        self.connections.remove(c)
        self.count = len(self.connections)
        
    def remove_node_connections(self, node_id, trace = None):
        log.log_trace(self, "is_node_multiconnection", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".remove_node_connections"}
        """
        Remove all connections to and from a given node.
        """
        if type(node_id) == list:
            for nid in node_id:
                self.remove_node_connections(nid, inf_trace)
        else:
            for c in self.get_connections(node_id, inf_trace):
                self.remove(c, inf_trace)
        
    def attr(self, attr):
        out = []
        if type(attr) == dict:
                out = [{getattr(n, k, None): getattr(n, attr[k], None) 
                        for n in self.connections} for k in attr.keys()]
        elif type(attr) == list:
            out = [[getattr(n, k, None) for k in attr] 
                   for n in self.connections]
        elif type(attr) == str:
            out = [getattr(n, attr, None) for n in self.connections]
        return out