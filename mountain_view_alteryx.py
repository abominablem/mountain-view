# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 21:44:21 2021

@author: marcu
@author: Marcus Hickman
@author: marhickman
"""

import xml.etree.ElementTree as et
from mh_logging import log
from nodes import Nodes, Node
from connections import Connections
from containers import Containers
import mv_formulas as mvf
from copy import deepcopy
from os import path
# from flow_diagram import FlowDiagram

"""
Development time:
    2021-07-28: 2 hours (22:30-00:30)
    2021-07-29: 2 hours (21:30-23:30)
    2021-07-30: 6 hours (19:30~02:30)
    2021-07-31: 2 hours
    2021-08-01: 3.5 hours
    2021-08-02: 4 hours
    2021-08-03: 2.75 hours
    2021-08-04: 1.5 hours
    2021-08-05: 0.75 hours
    2021-08-06: 
    2021-08-07: 
    2021-08-08: 
    2021-08-09: 
    2021-08-10: 
    2021-08-11: 
    2021-08-12: 
"""        

class Workflow:
    version = 0.1
    last_update = '2021-08-03'
    released = None
    testing_mode = True
    author = "Marcus Hickman <marhickman>"
    
    nodes = []
    connections = []
    containers = []
    xml = None
    # meta_workflows = {}
    
    def __init__(self, filepath, trace = None):
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".__init__"}
        log.log_trace(self, "__init__", trace)
        """
        Initiliase the Workflow object by parsing the given filepath as XML
        """
        self.name = self.__class__.__name__
        self.filepath = filepath
        self.name = path.splitext(path.basename(filepath))[0]
        
        with open(filepath, 'r') as ayx:
            self.raw_xml = ayx.read()
        
        self.xml = et.fromstring(self.raw_xml)
        
        self.version = self.xml.attrib["yxmdVer"]
        
        self.nodes = Nodes(self.xml, trace = inf_trace)
        self.connections = Connections(self.xml, trace = inf_trace)
        self.containers = Containers(self.xml, trace = inf_trace)
        
        for c in self.containers:
            #Add nodes within containers. These are contained within the
            #ChildNodes tag within the container Node
            if not c.disabled:
                self.nodes.add_nodes(xml = c.child_nodes_xml,
                                     parent_node = c,
                                     trace = inf_trace)
                
        self.formulas = self.get_formulas(trace = inf_trace)
        self.filters = self.get_filters(trace = inf_trace)
        self.selections = self.get_selections(trace = inf_trace)
        self.map_input_nodes(trace = inf_trace)
        self.map_output_nodes(trace = inf_trace)
        self.map_defined_input_nodes(trace = inf_trace)
        self.map_defined_output_nodes(trace = inf_trace)
        
        for n in self.nodes:
            n.is_multi_connection = self.connections.is_node_multiconnection(n.id)
        
    def get_formulas(self, trace = None):
        log.log_trace(self, "get_formulas", trace)
        """
        Extract a list of Formula dictionaries. Used to decide which fields to 
        analyse in the documentation.
        """
        arr_formulas = []
        for n in self.nodes:
            if n.is_decorator: continue
            if n.is_macro: continue
        
            if (n.type == 'AlteryxBasePluginsGui.Formula.Formula' or 
                n.type == 'LockInGui.LockInFormula.LockInFormula'):
                
                formulas = n.config.find('FormulaFields').findall('FormulaField')
                for i in range(len(formulas)):
                    f = formulas[i]
                    fdict = {'id': n.id,
                             'node': n,
                             'order_in_node': i,
                             'field': f.attrib['field'],
                             'expression': f.attrib['expression'],
                             'type': f.attrib['type'],
                             'size': f.attrib.get('size', None),
                             'context': None
                             }
                    arr_formulas.append(fdict)
                    
            elif n.type == 'AlteryxBasePluginsGui.MultiRowFormula.MultiRowFormula':
                fdict = {'id': n.id,
                         'node': n,
                         'order_in_node': 0,
                         'field': None,
                         'expression': None,
                         'type': None,
                         'size': None,
                         'context': None
                         }
                
                fdict['expression'] = n.config.find("Expression").attrib.get('value', 
                                                                             None)
                
                if n.config.find('UpdateField').attrib['value'] == 'True':
                    fdict['field'] = n.config.find('UpdateField_Name').text
                else:
                    fdict['field'] = n.config.find('CreateField_Name').text
                    fdict['type'] = n.config.find('CreateField_Type').text
                    fdict['size'] = n.config.find('CreateField_Size').text
                    fdict['context'] = {
                        "Rows that don't exist:": n.config.find('OtherRows').text,
                        'Group by': n.config.find('GroupByFields').text}
                arr_formulas.append(fdict)
                    
            elif n.type == 'AlteryxBasePluginsGui.MultiFieldFormula.MultiFieldFormula':
                fields = n.config.find("Fields")
                for i in range(len(fields)):
                    #selected keys have nothing. Unselected have selected = 
                    #"False"
                    field = fields[i]
                    try:
                        if field.attrib["selected"] == "False":
                            continue
                    except KeyError:
                        pass
                    fdict = {'id': n.id,
                             'node': n,
                             'order_in_node': i,
                             'field': field.attrib["name"],
                             'expression': n.config.find('Expression').text,
                             'type': None,
                             'size': None,
                             'context': None
                             }
                    if n.config.find('CopyOutput').attrib['value'] == 'True':
                        pass #TODO
                    else:
                        pass #TODO
                    arr_formulas.append(fdict)
                    
            elif n.type == 'AlteryxBasePluginsGui.DynamicRename.DynamicRename':
                if n.config.find("RenameMode").text == "Formula":
                    fdict = {'id': n.id,
                             'node': n,
                             'order_in_node': 0,
                             'field': "__FieldName__",
                             'expression': n.config.find("Expression").attrib.get("value", 
                                                                                  None),
                             'type': None,
                             'size': None,
                             'context': None
                             }
                    arr_formulas.append(fdict)
                    
            elif n.type == 'AlteryxBasePluginsGui.GenerateRows.GenerateRows':                
                fdict = {'id': n.id,
                         'node': n,
                         'order_in_node': 0,
                         'field': None,
                         'expression': n.config.find('Expression_Loop').text,
                         'type': None,
                         'size': None,
                         'context': {
                             "Initial value": n.config.find('Expression_Init').text,
                             "Loop condition:": n.config.find('Expression_Cond').text
                             }
                         }
                if n.config.find("UpdateField").attrib["value"] == "True":
                    fdict["field"] = n.config.find("UpdateField_Name").text
                else:
                    fdict["field"] = n.config.find("CreateField_Name").text
                    fdict["type"] = n.config.find("CreateField_Type").text
                    fdict["size"] = n.config.find("CreateField_Size").text
                arr_formulas.append(fdict)
                
            else:
                continue
        return arr_formulas
        
    def get_filters(self, trace = None):
        log.log_trace(self, "get_filters", trace)
        """
        Extract a list of Filter objects.
        """
        filters = []
        for n in self.nodes:
            if (n.type == "AlteryxBasePluginsGui.Filter.Filter" or 
                n.type == "LockInGui.LockInFilter.LockInFilter"):
                
                fdict = {'mode': n.config.find("Mode").text,
                         'field': None,
                         'expression': None
                         }
                if fdict['mode'] == 'Simple':
                    try:
                        fdict['field'] = n.config.find("Simple/Field").text
                    except AttributeError:
                        fdict['field'] = None
                    fdict['expression'] = n.annotation.default_text
                elif fdict['mode'] == 'Custom':
                    fdict['expression'] = n.config.find("Expression").text
                    fdict['field'] = mvf.fields_from_formula(fdict['expression'], 
                                                             trace = None)
                filters.append(fdict)
        return filters
    
    def get_selections(self, trace = None):
        log.log_trace(self, "get_filters", trace)
        """
        Extract a list of Selection objects.
        """
        selections = []
        for n in self.nodes:
            if (n.type == "AlteryxBasePluginsGui.AlteryxSelect.AlteryxSelect" or 
                n.type == "LockInGui.LockInSelect.LockInSelect"):
                
                for field in n.config.findall("SelectFields/SelectField"):
                    sdict = {'id': n.id,
                             'node': n,
                             'field': field.attrib["field"]}
                    
                    attributes = ['selected', 'rename', 'type', 'size']
                    for attr in attributes:
                        sdict[attr] = field.attrib.get(attr, None)
                        
                    if (sdict['selected'] == 'True' and sdict['rename'] is None
                        and sdict['type'] is None and sdict['size'] is None):
                        continue
                    else:
                        selections.append(sdict)
        return selections
                
    def map_input_nodes(self, trace = None):      
        log.log_trace(self, "map_input_nodes", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".map_input_nodes"}   
        """
        Updates the is_input property of each node object, using the simple
        node connection approximation.
        """
        self.input_nodes = []
        for n in self.nodes:
            if (self.connections.previous_node(n.id, trace = inf_trace) == [] 
                and not n.is_decorator):
                n.is_input = True
                self.input_nodes.append(n)
            else:
                n.is_input = False
                
    def map_output_nodes(self, trace = None):      
        log.log_trace(self, "map_output_nodes", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".map_output_nodes"}   
        """
        Updates the is_output property of each node object, using the simple
        node connection approximation.
        """
        self.output_nodes = []
        for n in self.nodes:
            if (self.connections.next_node(n.id, trace = inf_trace) == [] and
                not n.is_decorator and not n.is_browse):
                n.is_output = True
                self.output_nodes.append(n)
            else:
                n.is_output = False
                
    def map_defined_input_nodes(self, trace = None):      
        log.log_trace(self, "map_defined_input_nodes", trace)  
        """
        Updates the is_defined_input property of each node object, using the 
        defined list of input node types
        """
        for n in self.nodes:
            pass
            # if n.type in 
                
    def map_defined_output_nodes(self, trace = None):
        log.log_trace(self, "map_defined_output_nodes", trace) 
        """
        Updates the is_defined_output property of each node object, using the 
        defined list of output node types
        """
        for n in self.nodes:
            pass
            # if n.type in 
        
    def get_field_nodes(self, field, trace = None):
        log.log_trace(self, "get_field_nodes", trace)
        """
        Gets nodes dealing with the given field
        """
        nodes = []
        for f in self.formulas:
            if field in f["field"]:
                nodes.append(self.nodes.get_node(f["id"]))
        return nodes
    
    def copy(self, trace = None):
        log.log_trace(self, "copy", trace)
        return deepcopy(self)
                
    def remove_node(self, node_id, trace = None):
        log.log_trace(self, "previous_node", trace)
        inf_trace = {"source": "function call", 
                      "parent": self.name + ".remove_node"}
        """
        Remove all connections associated with a certain node.
        """
        n = self.nodes.get_node(node_id)
        if (n.is_input or n.is_output or n.is_multi_connection or 
            n.is_defined_input or n.is_defined_output):
            print("Warning: Node %s not removed. Node attribute " % node_id
                    + "overrides removal.")
        elif n.is_decorator:
            self.nodes.remove_node(node_id)
        else:         
            prev_nodes = self.connections.previous_node(node_id, inf_trace)
            if len(prev_nodes) > 1:
                print("Warning: Node %s not removed. Multiple " % node_id
                        + "incoming connections.")
            
            for c in self.connections.get_input_connections(node_id):
                self.connections.remove(c)
            
            prev_id = prev_nodes[0].id
            for c in self.connections.get_output_connections(node_id):
                c.origin.id = prev_id
            
            self.nodes.remove_node(node_id)
    
    def build_meta_workflow(self, field, trace = None):
        log.log_trace(self, "build_meta_workflow", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.name + ".build_meta_workflow"}
        """
        Build a meta-workflow for a given field by taking the existing workflow
        and removing all extraneous nodes and connections.
        
        Will always keep all inputs and outputs, and any nodes with multiple
        connections points
        """
        meta_workflow = self.copy(inf_trace)
        
        field_nodes = meta_workflow.get_field_nodes(field, inf_trace)
        field_nodes_id = [n.id for n in field_nodes]
        
        #counts of types of nodes for each container
        container_dict_field = {c.id: 0 for c in meta_workflow.containers}
        container_dict_node = {c.id: 0 for c in meta_workflow.containers}
        
        container_dict_field[None] = 0
        container_dict_node[None] = 0
        
        for n in meta_workflow.nodes.nodes[:]:
            cid = n.container.id if not n.container is None else None
            
            if n.is_output or n.is_input:
                container_dict_node[cid] += 1
                
            elif n.id in field_nodes_id:
                container_dict_node[cid] += 1
                container_dict_field[cid] += 1
                
            elif n.is_multi_connection:
                container_dict_node[cid] += 1
                
            elif field in n.fields:
                container_dict_node[cid] += 1
                container_dict_field[cid] += 1
                
            else:
                meta_workflow.remove_node(n.id, inf_trace)
            
        """Collapse container down if there are no field nodes within it.
        If there are external connections, create an input/output
        to the relevant nodes from the container"""
            
        for cont in container_dict_field.keys():
            if cont is None: continue
            container = meta_workflow.containers.get_container(cont)
            
            if container_dict_node[cont] == 0:
                #List of nodes IDs within the container
                con_nodes = container.nodes.attr("id")
                """ Remove all connections to and from the nodes within the
                container, then the container itself."""
                meta_workflow.connections.remove_node_connections(con_nodes)
                meta_workflow.nodes.remove_container(container, 
                                                      remove_container = True, 
                                                      minimise_container = False, 
                                                      trace = inf_trace)
                meta_workflow.containers.remove(cont, trace = inf_trace)
                
            elif container_dict_field[cont] == 0:
                con_nodes = container.nodes.attr("id")
                
                for c in meta_workflow.connections:
                    if (c.destination.id in con_nodes and not c.origin.id
                        in con_nodes):
                        c.destination.id = cont
                        c.destination.type = "ContainerInput"
                    elif (not c.destination.id in con_nodes and c.origin.id
                        in con_nodes):
                        c.origin.id = cont
                        c.origin.type = "ContainerOutput"
                    else:
                        continue
                meta_workflow.connections.remove_node_connections(con_nodes)
                meta_workflow.nodes.remove_container(container, 
                                                      remove_container = False, 
                                                      minimise_container = True, 
                                                      trace = inf_trace)
            else:
                pass
            
        return meta_workflow
                
    
if __name__ == "__main__":
    workflow = Workflow("..\\Workflows\\ar-sc.txt",
                        trace = {"source": "initialise class", 
                                 "parent": __name__})
    meta_workflow = workflow.build_meta_workflow("Check")