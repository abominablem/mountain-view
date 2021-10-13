# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 23:40:04 2021

@author: marcu
"""

from mh_logging import log
import ntpath
        
class Annotation:
    def __init__(self, xml, trace = None):
        log.log_trace(self, "__init__", trace)
        self.xml = xml.find("Annotation")
        self.annotation_xml = self.xml
        self.display_mode = self.xml.attrib["DisplayMode"]
        
        try:
            self.name = self.xml.find("Name").attrib["value"]
        except KeyError:
            self.name = None
            
        try:
            self.default_text = self.xml.find("DefaultAnnotationText").text
        except KeyError:
            self.default_text = ""
        
        self.flip_orientation = self.xml.find("Left").attrib["value"]
        
class Node:
    is_macro = False
    is_decorator = False
    is_input = False
    is_output = False
    is_multi_connection = False
    is_browse = False
    is_container = False
    fields = []
    is_defined_input = False
    is_defined_output = False
    container = None
    formula = None
    def __init__(self, xml, trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".__init__"}
        
        n = xml
        self.xml = xml
        self.id = n.attrib["ToolID"]
        self.gui_settings = n.find("GuiSettings")
        self.engine_settings = n.find("EngineSettings")
        self.properties = n.find("Properties")
        self.config = (None if self.properties is None 
                       else self.properties.find("Configuration"))
        
        if self.engine_settings is None:
            #no interaction with Alteryx engine = no impact on workflow
            #results
            self.is_decorator = True
        
        if not self.is_decorator:
            self.annotation = Annotation(self.properties, 
                                         trace = inf_trace)
            try:
                self.macro_path = self.engine_settings.attrib["Macro"]
                self.is_macro = True
                self.type = ntpath.basename(self.macro_path)
                # self.type = "__AlteryxMacro__"
            except KeyError:
                pass
        
        if not self.is_macro:
            self.type = self.gui_settings.attrib["Plugin"]
        
        if not self.is_macro and not self.is_decorator:
            self.engine_dll = self.engine_settings.attrib["EngineDll"]
            self.entry_point = self.engine_settings.attrib["EngineDllEntryPoint"]

        self.position = self.gui_settings.find("Position").attrib
        self.x = int(self.position['x'])
        self.y = int(self.position['y'])
        
        if self.type in ["AlteryxBasePluginsGui.BrowseV2.BrowseV2",
                         "LockInGui.LockInBrowse.LockInBrowse"]:
            self.is_browse = True
            
        elif self.type == "AlteryxGuiToolkit.ToolContainer.ToolContainer":
            self.is_container = True

class Nodes:
    def __init__(self, xml, node_tag = "Nodes", trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".__init__"}
        
        self.xml = xml
        self.nodes_dict = self.map_nodes(xml, node_tag, trace = inf_trace)
        self.nodes = list(self.nodes_dict.values())
        self.count = len(self.nodes)
    
    def __iter__(self):
        """
        Allow iteration of node object like "for n in Nodes". Equivalent to
        doing "for n in Nodes.nodes.values()"
        """
        self._i = -1
        return self
    
    def __next__(self):
        if self._i < self.count - 1:
            self._i += 1
            return self.nodes[self._i]
        else:
            raise StopIteration
    
    def map_nodes(self, xml, nodes_tag, trace = None):
        log.log_trace(self, "map_nodes", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".map_nodes"}
        """
        For a given ElementTree xml object, returns a dictionary of ToolIDs 
        and Node objects
        """
        search_tag = "Node" if (nodes_tag == "" 
                                or nodes_tag is None) else nodes_tag + "/Node"
        nd = {n.attrib['ToolID']: Node(n, trace = inf_trace)
              for n in xml.findall(search_tag)}
        return nd
    
    def get_node(self, node_id, trace = None):
        log.log_trace(self, "get_node", trace)
        """
        Return the Node object corresponding to node_id
        """
        return self.nodes_dict[node_id]
    
    def add_nodes(self, xml, parent_node = None, trace = None):
        log.log_trace(self, "add_nodes", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".add_nodes"}
        
        new_nodes = Nodes(xml, node_tag = "", trace = inf_trace)
        
        for n in new_nodes:
            n.container = parent_node
        
        self.nodes_dict = {**self.nodes_dict, **new_nodes.nodes_dict}
        self.nodes = self.nodes + new_nodes.nodes
        self.count = len(self.nodes)
        
    def remove_node(self, node_id, trace = None):
        log.log_trace(self, "remove_node", trace)
        """
        Remove all nodes with the given id(s)
        """
        if type(node_id) == str:
            node_id = [node_id]
        for n in self.nodes:
            if n.id in node_id: self.nodes.remove(n)
        self.count = len(self.nodes)
    
    def remove_container(self, c, remove_container = False, 
                         minimise_container = True, trace = None):
        log.log_trace(self, "remove_container", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".remove_container"}
        """
        Remove all nodes in the given container. Optionally remove the
        container itself as well, or shrink its size.
        """
        if remove_container:
            for n in self.nodes:
                if n.container == c: 
                    self.remove_node(n.id, trace = inf_trace)
            self.remove_node(c.id, trace = inf_trace)
        elif minimise_container:
            c.height = 20
            c.width = 150
        
    def get_nodes_attr(self, attrib, value, trace = None):
        log.log_trace(self, "get_nodes_attr", trace)
        """
        Get list of nodes where attribute matches the given value
        """
        nodes = []
        for n in self.nodes:
            if getattr(n, attrib, None) == value: 
                nodes.append(n)
        return nodes
    
    def attr(self, attr):
        """
        Get list/dictionary of attributes from all nodes.
        """
        out = []
        if type(attr) == dict:
                out = [{getattr(n, k, None): getattr(n, attr[k], None) 
                        for n in self.nodes} for k in attr.keys()]
        elif type(attr) == list:
            out = [[getattr(n, k, None) for k in attr] for n in self.nodes]
        elif type(attr) == str:
            out = [getattr(n, attr, None) for n in self.nodes]
        return out
    
    def max_position(self, xy):
        coords = self.attr(xy)
        return max(coords)
