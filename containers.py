# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 22:52:30 2021

@author: marcu
"""

from mh_logging import log
from nodes import Nodes, Node

class Container(Node):
    disabled = False
    folded = False
    fill_colour = '#ffffff'
    text_colour = '#000000'
    border_colour = '#314c4a'
    caption = None
    nodes = None
    def __init__(self, xml, trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".__init__"}
        
        #initialise parent Node class
        super(Container, self).__init__(xml)
        self.child_nodes_xml = self.xml.find('ChildNodes')
        self.nodes = Nodes(self.child_nodes_xml, node_tag = "", 
                           trace = inf_trace)
        
        self.disabled = (self.config.find("Disabled").attrib['value'] == "True")
        self.folded = (self.config.find("Folded").attrib['value'] == "True")
        
        self.width = int(self.position['width'])
        self.height = int(self.position['height'])
        
        self.style = self.config.find("Style")
        self.fill_colour = self.style.attrib["FillColor"]
        self.text_colour = self.style.attrib["TextColor"]
        self.border_colour = self.style.attrib["BorderColor"]
        
        self.caption = self.config.find("Caption").text
    
class Containers:
    containers = []
    def __init__(self, xml, trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".__init__"}
        
        self.xml = xml
        self.containers = self.map_containers(xml, inf_trace)
        self.containers_dict = {c.id: c for c in self.containers}
        self.count = len(self.containers)
    
    def __iter__(self):
        """
        Allow iteration of node object like "for n in Containers". Equivalent 
        to doing "for n in Containers.containers"
        """
        self._i = -1
        return self
    
    def __next__(self):
        if self._i < self.count - 1:
            self._i += 1
            return self.containers[self._i]
        else:
            raise StopIteration
            
    def get_container(self, node_id, trace = None):
        log.log_trace(self, "get_container", trace)
        return self.containers_dict[node_id]

    def map_containers(self, xml, trace = None):
        log.log_trace(self, "map_containers", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".map_containers"}
        """
        For a given ElementTree xml object, returns a dictionary of ToolIDs 
        and Node objects
        """
        containers = []
        for n in xml.findall("Nodes/Node"):
            node = Node(n, trace = inf_trace)
            if node.type == "AlteryxGuiToolkit.ToolContainer.ToolContainer":
                containers.append(Container(n, inf_trace))
        return containers
    
    def remove(self, container_id, trace = None):
        log.log_trace(self, "remove", trace)
        """
        Remove the container object with the given node id.
        """
        self.containers.remove(self.containers_dict[container_id])
        self.count -= 1
        
           